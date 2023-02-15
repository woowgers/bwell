import { on_event, logout } from "./helpers.js";

(function(){
  let logout_button = document.getElementById("navbar-logout-button");
  logout_button.addEventListener('click', on_event(logout, null));
})();
