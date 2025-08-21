// === АДАПТИВНЫЙ JavaScript ДЛЯ УЛУЧШЕНИЯ UX ===

document.addEventListener('DOMContentLoaded', function() {
    // Адаптация поиска для мобильных устройств
    adaptSearchForMobile();

    // Улучшение сайдбара для мобильных
    improveSidebarForMobile();

    // Адаптация таблиц
    adaptTablesForMobile();

    // Улучшение кнопок действий
    improveActionButtons();
});

// Адаптация поиска
function adaptSearchForMobile() {
    const searchForm = document.querySelector('#search-form');
    if (searchForm) {
        // Добавляем placeholder для мобильных
        const searchInput = searchForm.querySelector('input[type="text"]');
        if (searchInput) {
            searchInput.placeholder = 'Поиск...';
        }

        // Для мобильных устройств
        if (window.innerWidth <= 768) {
            searchForm.style.margin = '0.5rem 0';
            searchForm.style.width = '100%';

            const inputGroup = searchForm.querySelector('.input-group');
            if (inputGroup) {
                inputGroup.style.width = '100%';
                inputGroup.style.flexWrap = 'nowrap';
            }

            if (searchInput) {
                searchInput.style.flex = '1';
                searchInput.style.minWidth = '0';
            }

            const searchBtn = searchForm.querySelector('button');
            if (searchBtn) {
                searchBtn.style.flex = '0 0 auto';
            }
        }
    }
}

// Улучшение сайдбара для мобильных
function improveSidebarForMobile() {
    if (window.innerWidth <= 768) {
        // Скрываем сайдбар по умолчанию на мобильных
        const sidebar = document.querySelector('.main-sidebar');
        if (sidebar) {
            sidebar.style.transform = 'translateX(-100%)';
        }

        // Добавляем кнопку для открытия/закрытия сайдбара
        addMobileSidebarToggle();
    }
}

// Добавление кнопки переключения сайдбара
function addMobileSidebarToggle() {
    const navbar = document.querySelector('.main-header .navbar');
    if (navbar) {
        const toggleBtn = document.createElement('button');
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        toggleBtn.className = 'btn btn-sm btn-outline-secondary mr-2';
        toggleBtn.style.marginRight = '0.5rem';
        toggleBtn.onclick = function() {
            const sidebar = document.querySelector('.main-sidebar');
            if (sidebar) {
                sidebar.classList.toggle('sidebar-open');
            }
        };

        navbar.insertBefore(toggleBtn, navbar.firstChild);
    }
}

// Адаптация таблиц для мобильных
function adaptTablesForMobile() {
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (window.innerWidth <= 768) {
            // Добавляем горизонтальную прокрутку
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            wrapper.style.overflowX = 'auto';
            wrapper.style.webkitOverflowScrolling = 'touch';

            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Улучшение кнопок действий
function improveActionButtons() {
    const actionButtons = document.querySelectorAll('.btn');
    actionButtons.forEach(btn => {
        // Добавляем tooltips для кнопок без текста
        if (!btn.textContent.trim() && btn.querySelector('i')) {
            const icon = btn.querySelector('i');
            const iconClass = icon.className;

            if (iconClass.includes('fa-plus')) {
                btn.title = 'Добавить';
            } else if (iconClass.includes('fa-edit')) {
                btn.title = 'Редактировать';
            } else if (iconClass.includes('fa-trash')) {
                btn.title = 'Удалить';
            } else if (iconClass.includes('fa-eye')) {
                btn.title = 'Просмотреть';
            }
        }
    });
}

// Обработчик изменения размера окна
window.addEventListener('resize', function() {
    adaptSearchForMobile();
    adaptTablesForMobile();
});