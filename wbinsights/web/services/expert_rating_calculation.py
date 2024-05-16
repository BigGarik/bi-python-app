from dataclasses import dataclass
from django.db.models import Prefetch

from ..models import ExpertProfile


@dataclass
class ExpertProfileRow:
    expert_categories: list[str]
    consulting_experience: int
    experience: int
    hh_link: str
    linkedin_link: str
    is_verified: int


@dataclass
class ExpertEducationsRow:
    education_type: str
    specialized_education: bool
    educational_institution: str
    educational_institution_verified: bool
    diploma_number: int
    diploma_number_verified: bool


class ExpertRatingCalculation:
    def _extract_expert_educations(self, user_id: int) -> list[ExpertEducationsRow]:
        expert_profile = ExpertProfile.objects.prefetch_related(Prefetch('educations')).get(user__pk=user_id)
        return [
            ExpertEducationsRow(
                education_type=education.education_type,
                specialized_education=education.specialized_education,
                educational_institution=education.educational_institution,
                educational_institution_verified=education.educational_institution_verified,
                diploma_number=education.diploma_number,
                diploma_number_verified=education.diploma_number_verified
            )
            for education in expert_profile.educations.all()
        ]

    def _extract_expert_profile(self, user_id: int) -> ExpertProfileRow:
        expert_profile = ExpertProfile.objects.get(user__pk=user_id)
        return ExpertProfileRow(
            expert_categories=expert_profile.expert_categories,
            consulting_experience=expert_profile.consulting_experience,
            experience=expert_profile.experience,
            hh_link=expert_profile.hh_link,
            linkedin_link=expert_profile.linkedin_link,
            is_verified=expert_profile.is_verified
        )

    def _calculate_primary_education_rating(self, expert_educations: list[ExpertEducationsRow]) -> int:
        rating = 0
        # находим все основные образования эксперта
        for education_row in expert_educations:
            if education_row.education_type == 'primary' and education_row.specialized_education:
                # Проверяем статус верификации учебного заведения
                if education_row.educational_institution_verified:
                    # Проверяем статус верификации номера диплома
                    if education_row.diploma_number_verified:
                        rating += 2
                    # # Проверяем наличие верифицированных документов об образовании
                    # elif education_row.degree_documents.filter(is_verified=True).exists():
                    #     rating += 2
                    else:
                        rating += 1
        return rating

    def _calculate_additional_education_rating(self, expert_educations: list[ExpertEducationsRow]) -> int:
        rating = 0
        # Получаем все дополнительные образования эксперта, которые являются профильными
        for education_row in expert_educations:
            if education_row.education_type == 'additional' and education_row.specialized_education:
                # Проверяем, верифицировано ли учебное заведение
                if education_row.educational_institution_verified:
                    # # Проверяем, есть ли верифицированные документы об образовании
                    # if education_row.degree_documents.filter(is_verified=True).exists():
                    rating += 2
                else:
                    rating += 1
        return rating

    def _calculate_consulting_experience_rating(self, expert_profile: ExpertProfileRow) -> int:
        has_links_or_documents = expert_profile.hh_link or expert_profile.linkedin_link

        if expert_profile.consulting_experience >= 5:
            return 3
        elif expert_profile.consulting_experience >= 3 and has_links_or_documents:
            return 3
        elif expert_profile.consulting_experience >= 3:
            return 2
        elif expert_profile.consulting_experience >= 2 and has_links_or_documents:
            return 2
        else:
            return 0

    def _calculate_experience_rating(self, expert_profile: ExpertProfileRow) -> int:
        has_links_or_documents = expert_profile.hh_link or expert_profile.linkedin_link
        if expert_profile.experience >= 10:
            return 3
        elif expert_profile.experience >= 5 and has_links_or_documents:
            return 3
        elif expert_profile.experience >= 5:
            return 2
        elif expert_profile.experience >= 2 and has_links_or_documents:
            return 2
        elif expert_profile.experience >= 3:
            return 1
        elif expert_profile.experience >= 2 and has_links_or_documents:
            return 1
        else:
            return 0

    def calculate_rating(self, user_id: int) -> int:
        expert_profile: ExpertProfileRow = self._extract_expert_profile(user_id)
        expert_educations: list[ExpertEducationsRow] = self._extract_expert_educations(user_id)
        ratings: list[int] = [
            self._calculate_primary_education_rating(expert_educations),
            self._calculate_experience_rating(expert_profile),
            self._calculate_consulting_experience_rating(expert_profile),
            self._calculate_additional_education_rating(expert_educations),
            # Добавить сюда вызовы других методов расчета рейтинга по мере их создания
        ]
        return sum(ratings) if ratings else 0
