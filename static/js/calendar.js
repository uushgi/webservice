document.addEventListener('DOMContentLoaded', function() {
    const date = new Date();
    const currentMonth = date.getMonth();
    const currentYear = date.getFullYear();
    let selectedMonth = currentMonth;
    let selectedYear = currentYear;
    
    const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    
    const prevBtn = document.querySelector('.prev');
    const nextBtn = document.querySelector('.next');
    const monthTitle = document.querySelector('.month h1');
    const yearTitle = document.querySelector('.month p');
    const daysContainer = document.querySelector('.days');
    
    function renderCalendar(month, year) {
        const firstDay = new Date(year, month, 1).getDay();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        const daysInPrevMonth = new Date(year, month, 0).getDate();
        
        monthTitle.textContent = monthNames[month];
        yearTitle.textContent = year;
        
        let daysHtml = '';
        
        // предыдущий месяц
        for (let i = firstDay === 0 ? 6 : firstDay - 1; i > 0; i--) {
            daysHtml += `<div class="prev-date">${daysInPrevMonth - i + 1}</div>`;
        }
        
        // текущий месяц
        const today = new Date();
        for (let i = 1; i <= daysInMonth; i++) {
            const isToday = i === today.getDate() && 
                          month === today.getMonth() && 
                          year === today.getFullYear();
            
            let dayClass = isToday ? 'today' : '';
            
            daysHtml += `<div class="${dayClass}">${i}</div>`;
        }
        
        // следующий
        const totalCells = firstDay === 0 ? 42 : 35; // 6 или 5 строк
        const remainingCells = totalCells - (firstDay === 0 ? 6 : firstDay - 1) - daysInMonth;
        
        for (let i = 1; i <= remainingCells; i++) {
            daysHtml += `<div class="next-date">${i}</div>`;
        }
        
        daysContainer.innerHTML = daysHtml;
        
        addDayEventListeners();
    }
    
    prevBtn.addEventListener('click', function() {
        selectedMonth--;
        if (selectedMonth < 0) {
            selectedMonth = 11;
            selectedYear--;
        }
        renderCalendar(selectedMonth, selectedYear);
    });
    
    nextBtn.addEventListener('click', function() {
        selectedMonth++;
        if (selectedMonth > 11) {
            selectedMonth = 0;
            selectedYear++;
        }
        renderCalendar(selectedMonth, selectedYear);
    });
    
    function addDayEventListeners() {
        const days = document.querySelectorAll('.days div:not(.prev-date):not(.next-date)');
        const timeSlots = document.querySelector('.time-slots');
        const cancelBtn = document.querySelector('.cancel-btn');
        
        days.forEach(day => {
            day.addEventListener('click', function() {
                days.forEach(d => d.classList.remove('selected'));
                
                this.classList.add('selected');
                
                timeSlots.style.display = 'block';
            });
        });
        
        const timeSlotElements = document.querySelectorAll('.time-slot:not(.booked)');
        timeSlotElements.forEach(slot => {
            slot.addEventListener('click', function() {
                timeSlotElements.forEach(s => s.classList.remove('selected'));
                
                this.classList.add('selected');
            });
        });
        
        cancelBtn.addEventListener('click', function() {
            days.forEach(d => d.classList.remove('selected'));
            timeSlotElements.forEach(s => s.classList.remove('selected'));
            
            timeSlots.style.display = 'none';
        });
    }
    
    renderCalendar(currentMonth, currentYear);
}); 