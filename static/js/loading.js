function mostrarLoadingOverlay() {
    // Obtém referência para o elemento "loading-overlay"
    var loadingOverlay = document.getElementById('loading-overlay');
    
    // Altera o estilo para exibir o "loading-overlay"
    loadingOverlay.style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', function() {
    var links = document.querySelectorAll('.navigation a');
    for (var i = 0; i < links.length; i++) {
        links[i].addEventListener('click', mostrarLoadingOverlay);
    }
});