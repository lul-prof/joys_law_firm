document.addEventListener('DOMContentLoaded', function() {
    // Date input restrictions
    const dateInput = document.getElementById('date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    
    // Time input restrictions
    const timeInput = document.getElementById('time');
    timeInput.addEventListener('change', function() {
        const selectedTime = this.value;
        const hour = parseInt(selectedTime.split(':')[0]);
        
        // Restrict to business hours (9 AM - 5 PM)
        if (hour < 9 || hour >= 17) {
            alert('Please select a time between 9:00 AM and 5:00 PM');
            this.value = '';
        }
    });
    
    // Form validation
    const bookingForm = document.querySelector('form');
    bookingForm.addEventListener('submit', function(e) {
        const attorney = document.querySelector('select[name="attorney_id"]').value;
        if (!attorney) {
            e.preventDefault();
            alert('Please select an attorney');
        }
    });
});