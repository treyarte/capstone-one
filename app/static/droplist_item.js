$delete_item_btn = $('.delete-item-btn');

async function delete_item(e) {
  e.preventDefault();
  const item = e.target.parentNode.closest('.item');
  const droplist_id = item.dataset.droplist_id;
  const item_id = item.dataset.item_id;

  if ($(item).siblings().length === 1) {
    $location = $(item).siblings('.location');
    $location.parent().remove();
  }
  try {
    if ($(item).siblings().length === 1) {
      $location = $(item).siblings('.location');
      $location.parent().remove();
    } else {
      $(item).remove();
    }
    const resp = await axios.post(
      `${BASE_URL}/droplists/${droplist_id}/items/${item_id}/delete`
    );
  } catch (error) {
    console.error(error);
  }
}

$delete_item_btn.on('click', delete_item);
