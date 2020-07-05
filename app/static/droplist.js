$delete_droplist_btn = $('.delete-dl-btn');
async function delete_droplist(e) {
  e.preventDefault();
  const droplist = e.target.parentNode.parentNode.parentNode;
  const droplist_id = droplist.dataset.droplist_id;
  try {
    $(droplist).remove();
    const resp = await axios.post(
      `${BASE_URL}/droplists/${droplist_id}/delete`
    );
  } catch (error) {
    console.error(error);
  }
}

$delete_droplist_btn.on('click', delete_droplist);
