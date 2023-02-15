(function(){

function main()
{
  let forms = document.getElementsByTagName('form');

  if (forms.length == 0)
  {
    alert("No forms found from add-item-to-cart.js");
    return;
  }
  let form = forms[0];
  let number_input = null;
  let id_input = null;
  for (let child of form.children)
  {
    if (child.tagName == "input" && child.getAttribute("type") == "number")
      number_input = child;
    if (child.tagName == "input" && child.getAttribute("type") == "hidden")
      id_input = child;
  }
  if (number_input == null || id_input == null)
  {
    alert("No id input or number input found for cart from add-item-to-cart.js");
    return;
  }

  const url = window.origin + `/cart/add-item/${id_input.value}/${number_input.value}`;

  form.onsubmit = (_event) => {
    fetch(url, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({})
    });
  }
}


main();

})();
