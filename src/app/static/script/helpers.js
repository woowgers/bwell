export function on_event(fn, element)
{
  return (_event) => fn(element);
}

export async function logout()
{
  const url = window.location.origin + '/account/logout';
  await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    }
  ).then(res => {
    if (res.redirected)
      location.href = res.url;
  }, rej => {
    console.error(rej);
  })
}

export function remove_parent_node(element)
{
  element.parentNode.remove();
}

