// static/js/editor-init.js

// Wait for DOM and plugins to be loaded
window.addEventListener('load', function() {
    if (!window.pixabayPlugin) {
        console.error('Pixabay plugin not loaded!');
        return;
    }

    // Initialize the editor
    window.editor = grapesjs.init({
        container: '#gjs',
        fromElement: true,
        height: 'auto',
        width: 'auto',
        storageManager: {
            type: 'local',
            autoload: false,
            autosave: true,
            stepsBeforeSave: 1,
            id: 'gjs',
        },
        plugins: [window.pixabayPlugin],
        pluginsOpts: {
            [window.pixabayPlugin]: {
                pixabayApiKey: '47178532-a86b4337223bb283742a46665',
            }
        },
        panels: {defaults: []},
        blockManager: {
            appendTo: '#blocks',
            blocks: [
                {
                    id: 'sectionh5',
                    label: '<div class="t-class-comps">T1</div> <b style="color: #a5b1c8;">Большой Заголовок</b>',
                    attributes: {class: 'gjs-block-section'},
                    content: '<h1 style="font-family: sans-serif;">Insert large title text here</h1>',
                },
                {
                    id: 'sectionh3',
                    label: '<div class="t-class-comps">T3</div> <b style="color: #a5b1c8;">Средний Заголовок</b>',
                    attributes: {class: 'gjs-block-section'},
                    content: '<h3 style="font-family: sans-serif;">Insert medium title text here</h3>',
                },
                {
                    id: 'sectionh1',
                    label: '<div class="t-class-comps">T5</div> <b style="color: #a5b1c8;">Маленький Заголовок</b>',
                    attributes: {class: 'gjs-block-section'},
                    content: '<h4 style="font-family: sans-serif;">Insert small title text here</h4>',
                },
                {
                    id: 'text',
                    label: '<i class="bi bi-card-text" style="color: #a5b1c8; font-size: 30px; margin-bottom: 5px !important;"></i> <b style="color: #a5b1c8;">Текст</b>',
                    content: '<div data-gjs-type="text" style="font-family: sans-serif;">Insert your text here</div>',
                },
                {
                    id: 'image',
                    label: '<i class="bi bi-card-image" style="color: #a5b1c8; font-size: 30px; margin-bottom: 5px !important;"></i> <b style="color: #a5b1c8;">Изображение</b>',
                    select: true,
                    content: '<img src="placeholder-image.jpg" alt="Placeholder Image" style="max-width: 100%; height: auto; margin-top:5px;margin-bot:5px">',
                    activate: true,
                },
                {
                    id: 'list',
                    label: '<i class="bi bi-list" style="color: #a5b1c8; font-size: 30px; margin-bottom: 5px !important;"></i> <b style="color: #a5b1c8;">Список</b>',
                    content: '<ul><li style="padding: 5px 0;font-family: sans-serif;">Item 1</li><li style="font-family: sans-serif;">Item 2</li><li style="margin: 5px 0;font-family: sans-serif;">Item 3</li><li style="margin: 5px 0;font-family: sans-serif;">Item 4</li></ul>'
                },
                {
                    id: 'hr',
                    label: '<i class="bi bi-dash" style="color: #a5b1c8; font-size: 30px; margin-bottom: 5px !important;"></i> <b style="color: #a5b1c8; font-family: sans-serif;">Горизонтальная линия</b>',
                    content: '<hr>',
                },
                {
                    id: 'line_break',
                    label: '<i class="bi bi-arrows-expand" style="color: #a5b1c8;margin-bottom: 5px;font-size: 30px;"></i> <b style="color: #a5b1c8; font-family: sans-serif;">Разделитель</b>',
                    content: '<div style="margin-bottom: 10px;">&nbsp;</div>',
                }
            ]
        },
        styleManager: {
            appendTo: '#style-manager-container',
            sectors: [
                {
                    name: 'Typography',
                    open: true,
                    buildProps: ['font-family', 'font-size', 'font-weight', 'line-height', 'letter-spacing', 'color'],
                },
                {
                    name: 'Alignment',
                    open: false,
                    buildProps: ['text-align'],
                },
            ]
        }
    });

    // Editor load event
    editor.on('load', () => {
        const gjsContainer = document.getElementById('gjs');
        if (gjsContainer) {
            gjsContainer.style.overflow = 'visible';
            gjsContainer.style.height = '100%';
            gjsContainer.style.minHeight = '1000px';
        }

        const wrapper = editor.getWrapper();
        if (wrapper) {
            wrapper.setStyle({
                padding: '15px'
            });
        }

        // Set initial content if exists
        const contentInput = document.querySelector('input[name=content]');
        const stylesInput = document.querySelector('input[name=styles]');

        if (contentInput && contentInput.value) {
            editor.setComponents(contentInput.value);
        }
        if (stylesInput && stylesInput.value) {
            editor.setStyle(stylesInput.value);
        }
    });
});