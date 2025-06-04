// Elementos DOM principales
const sliderBar = document.getElementById('admin-slider-bar');
const btnMobileActivateSliderbar = document.getElementById('mobile-btn-activate-sliderbar');
const btnDesktopActivateSliderbar = document.getElementById('desktop-btn-activate-sliderbar');
const hiddenElements = document.querySelectorAll('.d-block');
const linkElements = document.querySelectorAll('#link');
const navLink = document.querySelector('.nav-link');
const faqButton = document.getElementById('btn_collapse');
const collapseLinks = document.querySelectorAll('#collapseQuestion1 > a, #collapseQuestion1 div > a');

// Estado del slider
let isSliderBarActive = false;

/**
 * Aplica el padding a los enlaces basado en el estado del slider
 * @param {boolean} isActive - Estado actual del slider
 */
const updateLinkspadding = (isActive) => {
    collapseLinks.forEach(link => {
        link.classList.toggle('ps-5', isActive);
    });
};

/**
 * Actualiza los estilos de visualización de los elementos ocultos
 */
const toggleHiddenElements = () => {
    hiddenElements.forEach(element => {
        element.classList.toggle('d-none');
    });
};

/**
 * Maneja los cambios de estilo cuando se activa/desactiva el slider
 */
const handleSliderBarToggle = () => {
    isSliderBarActive = !isSliderBarActive;

    // Toggle clases del slider
    sliderBar.classList.toggle('admin-slider-bar-open');
    sliderBar.classList.toggle('admin-slider-bar-close');

    // Actualizar padding de enlaces
    updateLinkspadding(isSliderBarActive);

    // Actualizar estilos de los elementos link
    linkElements.forEach(element => {
        element.classList.toggle('flex-column');
        element.classList.toggle('fs-9');
        element.classList.toggle('fs-6');
    });

    // Toggle clases de navegación
    navLink.classList.toggle('px-2');
    navLink.classList.toggle('px-1');
};

// Inicialización
toggleHiddenElements();

// Event Listeners
btnMobileActivateSliderbar.addEventListener('click', handleSliderBarToggle);
btnDesktopActivateSliderbar.addEventListener('click', handleSliderBarToggle);
faqButton.addEventListener('click', () => updateLinkspadding(isSliderBarActive));