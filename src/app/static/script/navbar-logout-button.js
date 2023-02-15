import { on_event, logout } from "./helpers.js";


function main()
{
  let logout_button = document.getElementById("navbar-logout-button");
  if (logout_button != null)
    logout_button.addEventListener('click', on_event(logout, null));
}

main();
