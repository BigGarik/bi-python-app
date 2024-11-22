
window.pixabayPlugin = (editor, opts = {}) => {
    console.log('Pixabay Plugin initialized with options:', opts);

    const options = {
        ...{
            pixabayApiKey: '47178532-a86b4337223bb283742a46665',
            blockLabel: '<i class="bi bi-images" style="color: #a5b1c8; font-size: 30px; margin-bottom: 5px !important;"></i> <b style="color: #a5b1c8;">Pixabay</b>',
            modalTitle: {
                en: 'Select Image from Pixabay',
                ru: 'Выбрать изображение из Pixabay'
            },
            searchPlaceholder: {
                en: 'Search images...',
                ru: 'Поиск изображений...'
            },
            defaultSearch: '',
            perPage: 20
        },
        ...opts
    };

    // define default content
    const defaultContent = {
        tagName: 'div',
        type: 'pixabay-image',
        content: `
            <div class="pixabay-placeholder" style="
                width: 100%;
                min-height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-direction: column;
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 4px;
                cursor: pointer;
            ">
                <i class="bi bi-images" style="font-size: 2em; color: #6c757d; margin-bottom: 10px;"></i>
                <div style="color: #6c757d;">Click to browse Pixabay images</div>
            </div>
        `,
        style: {
            width: '100%',
            'margin-top': '5px',
            'margin-bottom': '5px'
        },
        attributes: {
            'class': 'pixabay-image-container',
            'data-gjs-type': 'pixabay-image'
        }
    };

    // add custom block
    editor.BlockManager.add('pixabay-image-block', {
        label: options.blockLabel,
        category: 'Media',
        content: defaultContent,
        select: true,
        activate: true,
    });

    // definition of component
    editor.DomComponents.addType('pixabay-image', {
        isComponent: el => {
            if (el.getAttribute && el.getAttribute('data-gjs-type') === 'pixabay-image') {
                return { type: 'pixabay-image' }; // TODO: change later to just image and replace with default image
            }
        },
        model: {
            defaults: {
                ...defaultContent,
                droppable: false,
                hoverable: true,
                traits: [
                    {
                        type: 'button',
                        label: 'Browse Pixabay',
                        name: 'pixabay-browse',
                        text: 'Select Image',
                        full: true,
                        command: 'open-pixabay-modal'
                    },
                    {
                        type: 'text',
                        label: 'Alt Text',
                        name: 'alt'
                    }
                ]
            },

            init() {
                this.on('change:attributes:src', this.handleSrcChange);
            },

            handleSrcChange() {
                const src = this.get('attributes').src;
                if (src) {
                    this.set('content', `
                        <img 
                            src="${src}" 
                            alt="${this.get('attributes').alt || ''}"
                            style="max-width: 100%; height: auto; border-radius: 4px;"
                        />
                    `);
                } else {
                    this.set('content', defaultContent.content);
                }
            }
        },
        view: {
            events: {
                click: 'onClick',
                dblclick: 'onClick'
            },

            init() {
                this.listenTo(this.model, 'change:content', this.updateContent);
            },

            onClick(e) {
                e.preventDefault();
                editor.runCommand('open-pixabay-modal');
            },

            updateContent() {
                this.el.innerHTML = this.model.get('content');
            }
        }
    });

    // Pixabay Modal Command
    editor.Commands.add('open-pixabay-modal', {
        run(editor) {
            const modal = editor.Modal;
            const currentLocale = editor.I18n?.getLocale() || 'en';

            const container = document.createElement('div');
            container.className = 'pixabay-browser';

            const searchContainer = document.createElement('div');
            searchContainer.className = 'pixabay-search';
            searchContainer.innerHTML = `
                <input type="text" placeholder="${options.searchPlaceholder[currentLocale]}" class="pixabay-search-input" />
                <button class="pixabay-search-button">${currentLocale === 'en' ? 'Search' : 'Поиск'}</button>
            `;

            const imagesGrid = document.createElement('div');
            imagesGrid.className = 'pixabay-images-grid';

            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'pixabay-loading';
            loadingDiv.innerHTML = currentLocale === 'en' ? 'Loading images...' : 'Загрузка изображений...';

            container.appendChild(searchContainer);
            container.appendChild(loadingDiv);
            container.appendChild(imagesGrid);

            const fetchPixabayImages = async (query) => {
                loadingDiv.style.display = 'block';
                imagesGrid.innerHTML = '';

                try {
                    const response = await fetch(
                        `https://pixabay.com/api/?key=${options.pixabayApiKey}&q=${encodeURIComponent(query)}&per_page=${options.perPage}`
                    );
                    const data = await response.json();

                    loadingDiv.style.display = 'none';

                    data.hits.forEach(image => {
                        const imgWrapper = document.createElement('div');
                        imgWrapper.className = 'pixabay-image-wrapper';

                        const img = document.createElement('img');
                        img.src = image.previewURL;
                        img.alt = image.tags;

                        img.onclick = () => {
                            const selectedComponent = editor.getSelected();
                            if (selectedComponent && selectedComponent.get('type') === 'pixabay-image') {
                                selectedComponent.set('attributes', {
                                    ...selectedComponent.get('attributes'),
                                    src: image.webformatURL,
                                    alt: image.tags,
                                    'data-pixabay-id': image.id
                                });
                            }
                            modal.close();
                        };

                        imgWrapper.appendChild(img);
                        imagesGrid.appendChild(imgWrapper);
                    });
                } catch (error) {
                    console.error('Pixabay API Error:', error);
                    imagesGrid.innerHTML = currentLocale === 'en'
                        ? 'Error loading images. Please try again.'
                        : 'Ошибка загрузки изображений. Попробуйте еще раз.';
                }
            };

            const searchInput = searchContainer.querySelector('.pixabay-search-input');
            const searchButton = searchContainer.querySelector('.pixabay-search-button');

            searchButton.onclick = () => fetchPixabayImages(searchInput.value || options.defaultSearch);
            searchInput.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    fetchPixabayImages(searchInput.value || options.defaultSearch);
                }
            };

            // Initial load
            fetchPixabayImages(options.defaultSearch);

            // open modal when dragged into gjs
            modal.setTitle(options.modalTitle[currentLocale]);
            modal.setContent(container);
            modal.open();

            // Add styles
            const style = document.createElement('style');
            style.innerHTML = `
                .pixabay-browser {
                    padding: 20px;
                    font-family: sans-serif;
                }
                .pixabay-search {
                    margin-bottom: 20px;
                    display: flex;
                    gap: 10px;
                }
                .pixabay-search-input {
                    flex-grow: 1;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                }
                .pixabay-search-button {
                    padding: 8px 16px;
                    background: #4a90e2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .pixabay-search-button:hover {
                    background: #357abd;
                }
                .pixabay-images-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 15px;
                    max-height: 400px;
                    overflow-y: auto;
                }
                .pixabay-image-wrapper {
                    position: relative;
                    padding-bottom: 100%;
                    cursor: pointer;
                }
                .pixabay-image-wrapper img {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 4px;
                    transition: transform 0.2s;
                }
                .pixabay-image-wrapper img:hover {
                    transform: scale(1.05);
                }
                .pixabay-loading {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                }
            `;
            container.appendChild(style);
        }
    });
};

// Export the plugin
// export default pixabayPlugin;