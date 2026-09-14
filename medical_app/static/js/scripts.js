/* =========================================
   MEDCARE JAVASCRIPT
========================================= */


document.addEventListener("DOMContentLoaded", function () {


    /* =====================================
       NAVBAR ACTIVE LINK
    ===================================== */

    const menuLinks =
        document.querySelectorAll(".menu-link");


    menuLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            menuLinks.forEach(function (item) {

                item.classList.remove("active");

            });

            link.classList.add("active");

        });

    });


    /* =====================================
       USER DROPDOWN
    ===================================== */

    const userButton =
        document.querySelector(".user-btn");

    const userMenu =
        document.querySelector(".user-menu");


    if (userButton && userMenu) {

        userButton.addEventListener("click", function (event) {

            event.stopPropagation();

            userMenu.classList.toggle("show");

        });


        document.addEventListener("click", function () {

            userMenu.classList.remove("show");

        });

    }


    /* =====================================
       SMOOTH SCROLL
    ===================================== */

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {

        link.addEventListener("click", function (event) {

            const target =
                document.querySelector(
                    link.getAttribute("href")
                );


            if (target) {

                event.preventDefault();

                target.scrollIntoView({

                    behavior: "smooth",

                    block: "start"

                });

            }

        });

    });


    /* =====================================
       BUTTON HOVER EFFECT
    ===================================== */

    const buttons =
        document.querySelectorAll(
            ".action-btn, .login-btn, .brand-icon"
        );


    buttons.forEach(function (button) {

        button.addEventListener("mouseenter", function () {

            button.style.transition =
                "all 0.25s ease";

        });

    });

});