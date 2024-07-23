let tabs = document.getElementById('tabs');
if (tabs) {
   let childs = tabs.children;
   var currentElement = "1";
   let element = null;
   for (let i = 0; i < childs.length; i++) {
      childs[i].addEventListener('click', () => {
         for (let j = 0; j < childs.length; j++) {
            currentElement = childs[j].classList[0];
            element = document.getElementById(currentElement);
            element.style.display = "none";
            childs[j].classList.remove("active");
         }
         currentElement = childs[i].classList[0];
         element = document.getElementById(currentElement);
         element.style.display = "block";
         childs[i].classList.add("active");
      })
   }
}