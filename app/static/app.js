// const BASE_URL = 'http://localhost:5000/api';
const BASE_URL = 'https://mydroplist.herokuapp.com//api';

$graph = $('.all-forklifts');

$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

async function get_graph() {
  let status = $('#chart-status').val();
  let type = $('#chart-type').val();
  const resp = await axios.post(`${BASE_URL}/forklift_drivers/droplists`, {
    status,
    type,
  });
  $('.graph-content').empty().append(`<img src="${resp.data}" class="chart"/>`);
}

$graph.on('click', get_graph);
