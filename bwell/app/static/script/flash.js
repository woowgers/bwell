import { on_event, remove_parent_node } from "./helpers.js";


let ERROR_CONTAINER = document.getElementById("error-container");

if (ERROR_CONTAINER === null)
  alert("Failed to find #error-container.");


export function flash_success(message)
{
  const error_item = new DOMParser().parseFromString(`
    <div class="error-item">
      <p class="message-paragraph"> <i class="fa-solid fa-xmark"></i> ${message} </p>
    </div>
  `, 'text/html').body.firstChild;
  error_item.onclick = on_event(remove_parent_node, error_item);
  ERROR_CONTAINER.appendChild(error_item);
}


export function flash_info(message)
{
  const error_item = new DOMParser().parseFromString(`
    <div class="error-item">
      <p class="message-paragraph"> <i class="fa-solid fa-xmark"></i> ${message} </p>
    </div>
  `, 'text/html').body.firstChild;
  error_item.onclick = on_event(remove_parent_node, error_item);
  ERROR_CONTAINER.appendChild(error_item);
}


export function flash_error(message)
{
  const error_item = new DOMParser().parseFromString(`
    <div class="error-item">
      <p class="message-paragraph"> <i class="fa-solid fa-xmark"></i> ${message} </p>
    </div>
  `, 'text/html').body.firstChild;
  error_item.onclick = on_event(remove_parent_node, error_item);
  ERROR_CONTAINER.appendChild(error_item);
}


window.flash_success = flash_success;
window.flash_info = flash_info;
window.flash_error = flash_error;
