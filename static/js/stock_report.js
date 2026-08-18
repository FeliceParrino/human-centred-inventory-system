function formatDateValue(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function formatDateLabel(value) {
    if (!value) {
        return '';
    }

    const [year, month, day] = value.split('-');
    return `${day}/${month}/${year}`;
}

function createCalendar(picker) {
    const valueInput = picker.querySelector('[data-date-value]');
    const display = picker.querySelector('[data-date-display]');
    const calendar = picker.querySelector('[data-date-calendar]');
    const today = new Date();
    const selected = valueInput.value ? new Date(valueInput.value + 'T00:00:00') : today;
    let visibleMonth = selected.getMonth();
    let visibleYear = selected.getFullYear();

    function syncDisplay() {
        display.textContent = valueInput.value ? formatDateLabel(valueInput.value) : display.dataset.placeholder;
    }

    function renderCalendar() {
        const firstDay = new Date(visibleYear, visibleMonth, 1);
        const lastDay = new Date(visibleYear, visibleMonth + 1, 0);
        const startOffset = (firstDay.getDay() + 6) % 7;
        const monthName = firstDay.toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
        const selectedValue = valueInput.value;

        calendar.innerHTML = '';

        const header = document.createElement('div');
        header.className = 'calendar-header';

        const prevButton = document.createElement('button');
        prevButton.type = 'button';
        prevButton.className = 'calendar-nav';
        prevButton.textContent = '<';
        prevButton.addEventListener('click', () => {
            visibleMonth -= 1;
            if (visibleMonth < 0) {
                visibleMonth = 11;
                visibleYear -= 1;
            }
            renderCalendar();
        });

        const title = document.createElement('div');
        title.className = 'calendar-title';
        title.textContent = monthName;

        const nextButton = document.createElement('button');
        nextButton.type = 'button';
        nextButton.className = 'calendar-nav';
        nextButton.textContent = '>';
        nextButton.addEventListener('click', () => {
            visibleMonth += 1;
            if (visibleMonth > 11) {
                visibleMonth = 0;
                visibleYear += 1;
            }
            renderCalendar();
        });

        header.append(prevButton, title, nextButton);
        calendar.appendChild(header);

        const grid = document.createElement('div');
        grid.className = 'calendar-grid';

        ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].forEach(day => {
            const label = document.createElement('div');
            label.className = 'calendar-weekday';
            label.textContent = day;
            grid.appendChild(label);
        });

        for (let i = 0; i < startOffset; i += 1) {
            const empty = document.createElement('div');
            empty.className = 'calendar-empty';
            grid.appendChild(empty);
        }

        for (let day = 1; day <= lastDay.getDate(); day += 1) {
            const date = new Date(visibleYear, visibleMonth, day);
            const dateValue = formatDateValue(date);
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'calendar-day';
            button.textContent = String(day);

            if (dateValue === selectedValue) {
                button.classList.add('calendar-day-selected');
            }

            button.addEventListener('click', () => {
                valueInput.value = dateValue;
                syncDisplay();
                calendar.classList.remove('is-open');
                renderCalendar();
            });

            grid.appendChild(button);
        }

        calendar.appendChild(grid);
    }

    display.dataset.placeholder = display.textContent;
    display.addEventListener('click', () => {
        document.querySelectorAll('[data-date-calendar].is-open').forEach(openCalendar => {
            if (openCalendar !== calendar) {
                openCalendar.classList.remove('is-open');
            }
        });
        calendar.classList.toggle('is-open');
    });

    syncDisplay();
    renderCalendar();
}

document.querySelectorAll('[data-date-picker]').forEach(createCalendar);

document.addEventListener('click', event => {
    if (event.target.closest('[data-date-picker]')) {
        return;
    }

    document.querySelectorAll('[data-date-calendar].is-open').forEach(calendar => {
        calendar.classList.remove('is-open');
    });
});
