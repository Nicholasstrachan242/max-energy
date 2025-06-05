const loginForm = document.getElementById('loginForm');

loginForm.addEventListener('submit', function (event) {
  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value.trim();

  // Check if username and password are empty
  if (username === '' || password === '') {
    alert('Username and password are required.');
    event.preventDefault();
    return;
  }

  // Sanitize inputs
  const unsafePattern =
    /<|>|'|"|;|--|\b(OR|AND|SELECT|DROP|INSERT|DELETE|UPDATE|WHERE)\b/i;
  if (unsafePattern.test(username) || unsafePattern.test(password)) {
    alert('Invalid characters detected in username or password.');
    event.preventDefault();
    return;
  }
});
