const highlightActiveNavItem = () => {
  const navItems = document.querySelectorAll("#nav-sidebar > li > a");
  const currentPath = window.location.pathname;
  navItems.forEach((item) => {
    if (item.getAttribute("href") === currentPath) {
      item.classList.add("active");
    }
  });
};

highlightActiveNavItem();
