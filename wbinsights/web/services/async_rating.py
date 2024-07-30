import asyncio
import math

import asyncpg
from dataclasses import dataclass
import environs
import logging

env = environs.Env()
environs.Env.read_env()

db_user = env('USER_DB')
db_password = env('PASSWORD_DB')
db_host = env('URL_DB')
db_port = env('PORT_DB')
database = env('DATABASE')

logger = logging.getLogger(__name__)


@dataclass
class ExpertProfileRow:
    consulting_experience: int
    experience: int
    hh_link: str
    linkedin_link: str
    # is_verified: int


@dataclass
class ExpertEducationsRow:
    education_type: str
    specialized_education: bool
    educational_institution: str
    diploma_number: int


class ExpertRatingCalculation:
    async def write_to_database(self, conn, role_name, role_text, user_id, score):
        async with conn.transaction():
            rating_role_id = await conn.fetchrow(
                """
                INSERT INTO web_ratingrole (name, text) 
                VALUES ($1, $2) 
                ON CONFLICT (name) 
                DO UPDATE SET text = EXCLUDED.text
                RETURNING id
                """,
                role_name, role_text
            )
            await conn.execute(
                """
                INSERT INTO web_ratingcalculate (user_id, role_id, score) 
                VALUES ($1, $2, $3) 
                ON CONFLICT (user_id, role_id) 
                DO UPDATE SET score = EXCLUDED.score
                """,
                user_id, rating_role_id['id'], score
            )

    async def _extract_expert_educations(self, conn, user_id: int) -> list[ExpertEducationsRow]:
        async with conn.transaction():
            rows = await conn.fetch(
                """
                SELECT web_education.*
                FROM web_education
                JOIN web_expertprofile_education ON web_education.id = web_expertprofile_education.education_id
                JOIN web_expertprofile ON web_expertprofile_education.expertprofile_id = web_expertprofile.id
                WHERE web_expertprofile.user_id = $1
                """, user_id
            )
            return [
                ExpertEducationsRow(
                    education_type=row['education_type'],
                    specialized_education=row['specialized_education'],
                    educational_institution=row['educational_institution'],
                    diploma_number=row['diploma_number'],
                )
                for row in rows
            ]

    async def _extract_expert_profile(self, conn, user_id: int) -> ExpertProfileRow:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT * FROM web_expertprofile WHERE user_id=$1", user_id
            )
            return ExpertProfileRow(
                consulting_experience=row['consulting_experience'],
                experience=row['experience'],
                hh_link=row['hh_link'],
                linkedin_link=row['linkedin_link'],
                # is_verified=row['is_verified']
            )

    async def _calculate_primary_education_rating(self, conn, user_id: int,
                                                  expert_educations: list[ExpertEducationsRow]):
        score = 0
        for education_row in expert_educations:
            if education_row.education_type == 'primary' and education_row.specialized_education:
                if education_row.educational_institution:
                    if education_row.diploma_number:
                        score += 2
                    else:
                        score += 1
        role_name = 'calculate_primary_education_rating'
        role_text = 'Текст с условиями расчета основного образования'
        await self.write_to_database(conn, role_name, role_text, user_id, score)
        return {'score': score, 'max_score': 2}

    async def _calculate_additional_education_rating(self, conn, user_id: int,
                                                     expert_educations: list[ExpertEducationsRow]):
        score = 0
        for education_row in expert_educations:
            if education_row.education_type == 'additional' and education_row.specialized_education:
                if education_row.educational_institution:
                    score += 2
                else:
                    score += 1
        role_name = 'calculate_additional_education_rating'
        role_text = 'Текст с условиями расчета дополнительного образования'
        await self.write_to_database(conn, role_name, role_text, user_id, score)
        return {'score': score, 'max_score': 2}

    async def _calculate_consulting_experience_rating(self, conn, user_id: int,
                                                      expert_profile: ExpertProfileRow):
        has_links_or_documents = expert_profile.hh_link or expert_profile.linkedin_link
        if expert_profile.consulting_experience >= 5:
            score = 3
        elif expert_profile.consulting_experience >= 3 and has_links_or_documents:
            score = 3
        elif expert_profile.consulting_experience >= 3:
            score = 2
        elif expert_profile.consulting_experience >= 2 and has_links_or_documents:
            score = 2
        else:
            score = 0
        role_name = 'calculate_consulting_experience_rating'
        role_text = 'Текст с условиями расчета опыта консультаций'
        await self.write_to_database(conn, role_name, role_text, user_id, score)
        return {'score': score, 'max_score': 3}

    async def _calculate_experience_rating(self, conn, user_id: int, expert_profile: ExpertProfileRow):
        has_links_or_documents = expert_profile.hh_link or expert_profile.linkedin_link
        if expert_profile.experience >= 10:
            score = 3
        elif expert_profile.experience >= 5 and has_links_or_documents:
            score = 3
        elif expert_profile.experience >= 5:
            score = 2
        elif expert_profile.experience >= 2 and has_links_or_documents:
            score = 2
        elif expert_profile.experience >= 3:
            score = 1
        elif expert_profile.experience >= 2 and has_links_or_documents:
            score = 1
        else:
            score = 0
        role_name = 'calculate_experience_rating'
        role_text = 'Текст с условиями расчета опыта работы'
        await self.write_to_database(conn, role_name, role_text, user_id, score)
        return {'score': score, 'max_score': 3}

    async def calculate_rating(self, pool, user_id: int):
        async with pool.acquire() as conn:
            async with conn.transaction():
                expert_profile = await self._extract_expert_profile(conn, user_id)
                expert_educations = await self._extract_expert_educations(conn, user_id)
                rating1 = await self._calculate_primary_education_rating(conn, user_id, expert_educations)
                rating2 = await self._calculate_experience_rating(conn, user_id, expert_profile)
                rating3 = await self._calculate_consulting_experience_rating(conn, user_id, expert_profile)
                rating4 = await self._calculate_additional_education_rating(conn, user_id, expert_educations)
                sum_max_score = sum(
                    [rating1['max_score'], rating2['max_score'], rating3['max_score'], rating4['max_score']])
                sum_score = sum([rating1['score'], rating2['score'], rating3['score'], rating4['score']])
                rating = math.floor((sum_score / sum_max_score * 5) * 2) / 2
                await conn.fetch("UPDATE web_expertprofile SET rating = $1, points = $2 WHERE user_id = $3", rating, sum_score, user_id)


async def calculate_rating_for_all_experts():
    pool = await asyncpg.create_pool(
        user=db_user, password=db_password,
        database=database, host=db_host
    )
    async with pool.acquire() as conn:
        expert_ids = await conn.fetch("SELECT user_id FROM web_expertprofile")

    calculator = ExpertRatingCalculation()
    semaphore = asyncio.Semaphore(5)  # Ограничиваем количество одновременных задач до 5

    async def calculate_with_semaphore(user_id):
        async with semaphore:
            await calculator.calculate_rating(pool, user_id)

    tasks = [calculate_with_semaphore(expert_id['user_id']) for expert_id in expert_ids]
    await asyncio.gather(*tasks)

    await pool.close()  # Закрываем пул соединений после завершения всех задач
    logger.info('Rating calculation completed')


if __name__ == "__main__":
    asyncio.run(calculate_rating_for_all_experts())
