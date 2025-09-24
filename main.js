document.addEventListener('DOMContentLoaded', () => {
  const searchBar = document.getElementById('search-bar');
  const fileList = document.getElementById('file-list');
  
  // Verifica se os elementos existem antes de adicionar o listener
  if (searchBar && fileList) {
    const listItems = fileList.getElementsByTagName('li');

    searchBar.addEventListener('keyup', (event) => {
      const searchTerm = event.target.value.toLowerCase();
      
      for (let i = 0; i < listItems.length; i++) {
        const item = listItems[i];
        const itemName = item.textContent.toLowerCase();
        
        if (itemName.includes(searchTerm)) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      }
    });
  }
});