document.addEventListener('DOMContentLoaded', function() {
    let date = new Date();
    let currentMonth = date.getMonth();
    let currentYear = date.getFullYear();
    let selectedMonth = currentMonth;
    let selectedYear = currentYear;
    let selectedVenue = null;
    let selectedDate = null;
    let notificationTimeout = null;
    
    const monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                      "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
    
    let monthTitle = document.querySelector('.month h1');
    let yearTitle = document.querySelector('.month p');
    let daysContainer = document.querySelector('.days');
    let venueTabs = document.querySelectorAll('.venue-tab');
    let bookingForm = document.querySelector('form[name="booking"]');
    let timeSlots = document.querySelector('.time-slots');
    
    document.querySelector('.prev').addEventListener('click', () => {
        selectedMonth--;
        if (selectedMonth < 0) {
            selectedMonth = 11;
            selectedYear--;
        }
        renderCalendar(selectedMonth, selectedYear);
    });
    
    document.querySelector('.next').addEventListener('click', () => {
        selectedMonth++;
        if (selectedMonth > 11) {
            selectedMonth = 0;
            selectedYear++;
        }
        renderCalendar(selectedMonth, selectedYear);
    });
    
    venueTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            venueTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            selectedVenue = this.textContent;
            
            if (selectedDate) {
                updateBookedSlots(selectedVenue, selectedDate);
            }
            
            renderCalendar(selectedMonth, selectedYear);
        });
    });
    
    function renderCalendar(month, year) {
        let firstDay = new Date(year, month, 1).getDay();
        let daysInMonth = new Date(year, month + 1, 0).getDate();
        let daysInPrevMonth = new Date(year, month, 0).getDate();
        
        monthTitle.textContent = monthNames[month];
        yearTitle.textContent = year;
        
        let daysHtml = '';
        
        // месяцы до
        for (let i = firstDay === 0 ? 6 : firstDay - 1; i > 0; i--) {
            daysHtml += `<div class="prev-date">${daysInPrevMonth - i + 1}</div>`;
        }
        
        // актуальные
        let today = new Date();
        for (let i = 1; i <= daysInMonth; i++) {
            let isToday = i === today.getDate() && 
                         month === today.getMonth() && 
                         year === today.getFullYear();
            
            let currentDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
            // бд с нулями в дате, так что форматируем с нулями
            // может временное решение, может нет
            let isSelected = selectedDate === currentDate;
            
            daysHtml += `<div class="${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}" 
                             data-venue="${selectedVenue}" 
                             data-date="${currentDate}">${i}</div>`;
        }
        
        let totalCells = firstDay === 0 ? 42 : 35;
        let remainingCells = totalCells - (firstDay === 0 ? 6 : firstDay - 1) - daysInMonth;
        
        for (let i = 1; i <= remainingCells; i++) {
            daysHtml += `<div class="next-date">${i}</div>`;
        }
        
        daysContainer.innerHTML = daysHtml;
        addDayEventListeners();
    }
    

    async function updateBookedSlots(venue, date) {
        try {
            let response = await fetch(`/get-booked-slots?venue=${encodeURIComponent(venue)}&date=${encodeURIComponent(date)}`);
            let data = await response.json();
            
            if (data.error) {
                console.error('Error fetching booked slots:', data.error);
                return;
            }
            
            document.querySelectorAll('.time-slot').forEach(slot => {
                let time = slot.textContent.split(' - ')[0];
                if (data.booked_slots.includes(time)) {
                    slot.classList.add('booked');
                    slot.classList.remove('selected');
                } else {
                    slot.classList.remove('booked');
                }
            });
        } catch (error) {
            console.error('Error:', error);
        }
    }
    

    function showNotification(message) {
        const existingNotification = document.querySelector('.alert');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = 'alert alert-warning booking-notification';
        notification.textContent = message;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = () => notification.remove();
        
        notification.appendChild(closeBtn);
        document.querySelector('.notifications').appendChild(notification);

        if (notificationTimeout) {
            clearTimeout(notificationTimeout);
        }
        notificationTimeout = setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    function addDayEventListeners() {
        let days = document.querySelectorAll('.days div:not(.prev-date):not(.next-date)');
        let cancelBtn = document.querySelector('.cancel-btn');
        
        days.forEach(day => {
            day.addEventListener('click', function() {
                if (!selectedVenue) {
                    showNotification('Пожалуйста, сначала выберите площадку');
                    return;
                }
                
                days.forEach(d => d.classList.remove('selected'));
                this.classList.add('selected');
                
                selectedDate = this.getAttribute('data-date');
                timeSlots.style.display = 'block';
                timeSlots.setAttribute('data-venue', selectedVenue);
                timeSlots.setAttribute('data-date', selectedDate);
                
                updateBookedSlots(selectedVenue, selectedDate);
            });
        });
        
        document.querySelectorAll('.time-slot').forEach(slot => {
            slot.addEventListener('click', function() {
                if (this.classList.contains('booked')) {
                    showNotification('Это время уже забронировано');
                    return;
                }
                document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                this.classList.add('selected');
            });
        });
        
        cancelBtn.addEventListener('click', () => {
            days.forEach(d => d.classList.remove('selected'));
            document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
            timeSlots.style.display = 'none';
            selectedDate = null;
        });
    }
    

    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            let selectedDay = document.querySelector('.days div.selected');
            let selectedTimeSlot = document.querySelector('.time-slot.selected');
            
            if (!selectedDay || !selectedTimeSlot) {
                e.preventDefault();
                showNotification('Пожалуйста, выберите дату и время');
                return;
            }
            
            if (selectedTimeSlot.classList.contains('booked')) {
                e.preventDefault();
                showNotification('Это время уже забронировано');
                return;
            }
            
            this.appendChild(Object.assign(document.createElement('input'), {
                type: 'hidden',
                name: 'venue',
                value: selectedVenue
            }));
            
            this.appendChild(Object.assign(document.createElement('input'), {
                type: 'hidden',
                name: 'date',
                value: selectedDay.getAttribute('data-date')
            }));
            
            this.appendChild(Object.assign(document.createElement('input'), {
                type: 'hidden',
                name: 'time',
                value: selectedTimeSlot.textContent.split(' - ')[0]
            }));
        });
    }
    
    renderCalendar(currentMonth, currentYear);
}); 

