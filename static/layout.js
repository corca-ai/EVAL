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

const getNumber = (str) => Number(str.replace("px", ""));

function expandTextarea(id) {
  document.getElementById(id).addEventListener(
    "keyup",
    function () {
      this.style.overflow = "hidden";
      this.style.height =
        Math.max(getNumber(this.style.height), this.scrollHeight) + "px";
    },
    false
  );
}

expandTextarea("prompt");
