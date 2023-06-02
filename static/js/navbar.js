let menuToggle = document.querySelector('.toggle');
let navigation = document.querySelector('.navigation');

menuToggle.onclick = function() {
  menuToggle.classList.toggle('active');
  navigation.classList.toggle('active');

  if (navigation.classList.contains('active')) {
    navigation.style.display = 'block';
  } else {
    navigation.style.display = 'none';
  }
};

let list = document.querySelectorAll('.list');

for (let i = 0; i < list.length; i++) {
  let link = list[i].querySelector('a');
  let href = link.getAttribute('href');

  link.onclick = function(event) {
    event.preventDefault();
    window.location.href = href;

    for (let j = 0; j < list.length; j++) {
      list[j].classList.remove('active');
    }

    list[i].classList.add('active');
  };

  // Add the following code to check the current URL and apply the active class
  let currentURL = window.location.pathname;
  if (currentURL === href) {
    list[i].classList.add('active');
  }
}