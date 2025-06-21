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
            firstHalfIndex = null;
            lastHalfIndex = null;
            selectedHalfIndices = [];
            fullResetHalfSelection();
            venueTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            selectedVenue = this.dataset.venueId;
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
    
    let firstHalfIndex = null;
    let lastHalfIndex = null;
    let selectedHalfIndices = [];

    function updateSlotTextSelection() {
        document.querySelectorAll('.time-slot').forEach(slot => {
            const leftHalf = slot.querySelector('.slot-half.left');
            const rightHalf = slot.querySelector('.slot-half.right');
            const leftText = slot.querySelector('.slot-text.left');
            const rightText = slot.querySelector('.slot-text.right');
            const dashText = slot.querySelector('.slot-text.dash');
            const leftSelected = leftHalf.classList.contains('selected');
            const rightSelected = rightHalf.classList.contains('selected');
            
            leftText.classList.remove('selected');
            rightText.classList.remove('selected');
            dashText.classList.remove('selected');

            if (leftSelected && rightSelected) {
                leftText.classList.add('selected');
                rightText.classList.add('selected');
                dashText.classList.add('selected');
            } else if (leftSelected) {
                leftText.classList.add('selected');
            } else if (rightSelected) {
                rightText.classList.add('selected');
            }
        });
    }

    function fullResetHalfSelection() {
        document.querySelectorAll('.slot-half').forEach(s => s.classList.remove('selected'));
        firstHalfIndex = null;
        lastHalfIndex = null;
        selectedHalfIndices = [];
        updateSlotTextSelection();
    }

    function resetHalfSelection() {
        document.querySelectorAll('.slot-half').forEach(s => s.classList.remove('selected'));
        updateSlotTextSelection();
    }

    function getSlotHalves() {
        return Array.from(document.querySelectorAll('.slot-half'));
    }

    function addSlotHalfEventListeners() {
        getSlotHalves().forEach((half, idx) => {
            const newHalf = half.cloneNode(true);
            half.parentNode.replaceChild(newHalf, half);
        });
        getSlotHalves().forEach((half, idx) => {
            half.addEventListener('click', function() {
                if (half.classList.contains('booked')) {
                    showNotification('Это время уже забронировано');
                    return;
                }
                // первый клик
                if (firstHalfIndex === null) {
                    fullResetHalfSelection();
                    firstHalfIndex = idx;
                    half.classList.add('selected');
                    selectedHalfIndices = [idx];
                    updateSlotTextSelection();
                    return;
                }
                // второй клик
                if (lastHalfIndex === null) {
                    lastHalfIndex = idx;
                    let start = Math.min(firstHalfIndex, lastHalfIndex);
                    let end = Math.max(firstHalfIndex, lastHalfIndex);
                    let range = [];
                    let hasBooked = false;
                    getSlotHalves().forEach((s, i) => {
                        if (i >= start && i <= end) {
                            if (s.classList.contains('booked')) {
                                hasBooked = true;
                            }
                            range.push(i);
                        }
                    });
                    if (hasBooked) {
                        showNotification('В выбранном диапазоне есть занятые слоты');
                        fullResetHalfSelection();
                        return;
                    }
                    if (range.length > 6) {
                        showNotification('Нельзя выбрать больше 3 часов подряд');
                        fullResetHalfSelection();
                        return;
                    }
                    range.forEach(i => getSlotHalves()[i].classList.add('selected'));
                    selectedHalfIndices = range;
                    updateSlotTextSelection();
                    return;
                }
                // третий клик сброс
                resetHalfSelection();
                firstHalfIndex = idx;
                lastHalfIndex = null;
                selectedHalfIndices = [idx];
                half.classList.add('selected');
                updateSlotTextSelection();
            });
        });
    }

    async function updateBookedSlots(venue, date) {
        try {
            let response = await fetch(`/get-booked-slots?venue=${encodeURIComponent(venue)}&date=${encodeURIComponent(date)}`);
            let data = await response.json();
            if (data.error) {
                console.error('Error fetching booked slots:', data.error);
                return;
            }
            document.querySelectorAll('.slot-half').forEach(half => {
                let time = half.getAttribute('data-time');
                if (data.booked_slots.includes(time)) {
                    half.classList.add('booked');
                    half.classList.remove('selected');
                } else {
                    half.classList.remove('booked');
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

                firstHalfIndex = null;
                lastHalfIndex = null;
                selectedHalfIndices = [];
                fullResetHalfSelection();
                addSlotHalfEventListeners();
            });
        });
        cancelBtn.addEventListener('click', () => {
            days.forEach(d => d.classList.remove('selected'));
            fullResetHalfSelection();
            timeSlots.style.display = 'none';
            selectedDate = null;
        });
    }
    

    // --- SUBMIT FORM WITH ARRAY OF TIMES ---
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            let selectedDay = document.querySelector('.days div.selected');
            let halves = getSlotHalves().filter(s => s.classList.contains('selected'));
            if (!selectedDay || halves.length === 0) {
                e.preventDefault();
                showNotification('Пожалуйста, выберите дату и время');
                return;
            }
            let times = halves.map(h => h.getAttribute('data-time'));
            Array.from(this.querySelectorAll('input[name="times[]"]')).forEach(i => i.remove());
            times.forEach(t => {
                this.appendChild(Object.assign(document.createElement('input'), {
                    type: 'hidden',
                    name: 'times[]',
                    value: t
                }));
            });
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
        });
    }
    
    renderCalendar(currentMonth, currentYear);
}); 

