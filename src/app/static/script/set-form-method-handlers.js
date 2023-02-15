
function set_form_method_handlers()
{
  let forms = document.getElementsByTagName("form");

  for (let form of forms)
  {
    let form_method = form.getAttribute('method').toUpperCase();
    let form_action = form.getAttribute('action');
    if (form_method != "GET" && form_method != "POST" && form_method != "HEAD")
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        fetch(
          form_action,
          {
            method: form_method,
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            body: new FormData(form),
          }
        ).then(response => console.info(response));
      });
  }
}

window.addEventListener('load', () => {
  set_form_method_handlers();
});
