document.addEventListener('DOMContentLoaded', () => {
  const searchBar = document.getElementById('search-bar');
  const fileList = document.getElementById('file-list');

  if (searchBar && fileList) {
    const listItems = fileList.getElementsByTagName('li');

    searchBar.addEventListener('keyup', (event) => {
      const searchTerm = event.target.value.toLowerCase().trim(); // Use trim() aqui também, por segurança
      
      for (let i = 0; i < listItems.length; i++) {
        const item = listItems[i];
        
        // 1. Encontra a tag <a> dentro do <li>
        const linkElement = item.querySelector('a'); 
        
        let itemName = "";
        if (linkElement) {
            // 2. Lê o texto, converte para minúsculas E REMOVE ESPAÇOS EXTRAS
            itemName = linkElement.textContent.toLowerCase().trim(); 
        }

        // 3. Verifica se o nome do item inclui o termo de pesquisa
        if (itemName.includes(searchTerm)) {
          item.style.display = 'flex'; 
        } else {
          item.style.display = 'none';
        }
      }
    });
  }
});