document.addEventListener('DOMContentLoaded', function() {
  var submitBtn = document.getElementById('submitBtn');
  var checkbox = document.getElementById('condition1');
  var form = document.querySelector('form');

  // Add event listener for form submission
  form.addEventListener('submit', function(event) {
      // Check if checkbox is checked
      if (!checkbox.checked) {
          // Prevent default form submission behavior
          event.preventDefault();
          // Display alert message
          alert('Please acknowledge the terms and conditions.');
      }
  });

  // Add event listener for button click
  submitBtn.addEventListener('click', function() {
      // Check if checkbox is checked
      if (checkbox.checked) {
          
      } else {
          // Display alert message
          alert('Please acknowledge the terms and conditions.');
      }
  });
});
