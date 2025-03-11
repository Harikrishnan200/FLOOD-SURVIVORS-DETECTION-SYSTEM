const navbar = document.getElementById('navbar');
const toggleSidebar = document.getElementById('toggleSidebar');
const menuToggle = document.getElementById('menuToggle');
const toggleTheme = document.getElementById('toggleTheme');
const html = document.documentElement;
const mainContent = document.querySelector('.ml-64');

toggleSidebar.addEventListener('click', () => {
    navbar.classList.toggle('w-20');
    navbar.classList.toggle('w-64');
    mainContent.classList.toggle('ml-20');
    mainContent.classList.toggle('ml-64');
    const isCollapsed = navbar.classList.contains('w-20');
    document.querySelectorAll('#navbar span, #navbar h2, #navbar .ml-3').forEach(el => {
        el.style.display = isCollapsed ? 'none' : 'block';
    });
    document.querySelector('#navbar input').placeholder = isCollapsed ? '' : 'Search';
});

menuToggle.addEventListener('click', () => {
    navbar.classList.toggle('-translate-x-full');
});

toggleTheme.addEventListener('click', () => {
    html.classList.toggle('dark');
    const isDark = html.classList.contains('dark');
    toggleTheme.innerHTML = isDark ? '<i class="ri-moon-line text-xl text-white"></i>' : '<i class="ri-sun-line text-xl"></i>';
    localStorage.theme = isDark ? 'dark' : 'light';
});

// Check for saved theme preference or use system preference
if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    html.classList.add('dark');
} else {
    html.classList.remove('dark');
}

// Update theme icon on load
const isDark = html.classList.contains('dark');
toggleTheme.innerHTML = isDark ? '<i class="ri-moon-line text-xl text-white"></i>' : '<i class="ri-sun-line text-xl"></i>';

// const navbar = document.getElementById('navbar');
// const toggleSidebar = document.getElementById('toggleSidebar');
// const menuToggle = document.getElementById('menuToggle');
// const toggleTheme = document.getElementById('toggleTheme');
// const html = document.documentElement;
// const mainContent = document.querySelector('.ml-64');

// // Navbar functionality
// toggleSidebar.addEventListener('click', () => {
//     navbar.classList.toggle('w-20');
//     navbar.classList.toggle('w-64');
//     mainContent.classList.toggle('ml-20');
//     mainContent.classList.toggle('ml-64');
//     const isCollapsed = navbar.classList.contains('w-20');
//     document.querySelectorAll('#navbar span, #navbar h2, #navbar .ml-3').forEach(el => {
//         el.style.display = isCollapsed ? 'none' : 'block';
//     });
//     document.querySelector('#navbar input').placeholder = isCollapsed ? '' : 'Search';
// });

// menuToggle.addEventListener('click', () => {
//     navbar.classList.toggle('-translate-x-full');
// });

// // Day and night mode functionality
// toggleTheme.addEventListener('click', () => {
//     html.classList.toggle('dark');
//     const isDark = html.classList.contains('dark');
//     toggleTheme.innerHTML = isDark ? '<i class="ri-sun-line text-xl"></i>' : '<i class="ri-moon-line text-xl text-white"></i>';
//     localStorage.theme = isDark ? 'dark' : 'light';
// });

// // Check for saved theme preference or use system preference
// if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
//     html.classList.add('dark');
// } else {
//     html.classList.remove('dark');
// }

// // Update theme icon on load
// const isDark = html.classList.contains('dark');
// toggleTheme.innerHTML = isDark ? '<i class="ri-sun-line text-xl"></i>' : '<i class="ri-moon-line text-xl text-white"></i>';

// // Highlighting functionality for navbar buttons
// const navbarButtons = document.querySelectorAll('.navbar-button');

// navbarButtons.forEach(button => {
//     button.addEventListener('click', () => {
//         // Remove 'active' class from all buttons
//         navbarButtons.forEach(btn => btn.classList.remove('active'));
//         // Add 'active' class to the clicked button
//         button.classList.add('active');
//     });
// });