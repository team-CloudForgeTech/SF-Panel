const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const sidebarToggle = document.getElementById('sidebar-toggle');

sidebar.addEventListener('mouseenter', () => {
    sidebar.classList.add('expanded');
    mainContent.classList.add('expanded');
});

sidebar.addEventListener('mouseleave', () => {
    sidebar.classList.remove('expanded');
    mainContent.classList.remove('expanded');
});

// 侧边栏切换按钮功能
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('expanded');
    mainContent.classList.toggle('expanded');
});
