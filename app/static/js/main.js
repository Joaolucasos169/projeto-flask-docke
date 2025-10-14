// Função central que usa WebRTC para tentar descobrir o IP real (LAN/público)
function getLocalIPs(callback) {
    // A técnica WebRTC força a negociação de IP.
    const pc = new RTCPeerConnection({ iceServers: [] });
    let ips = {};
    
    // Adiciona um manipulador para candidatos ICE (onde o IP é revelado)
    pc.onicecandidate = function(ice) {
        if (!ice || !ice.candidate || !ice.candidate.candidate) return;
        
        // Expressão regular para extrair IPs válidos (IPv4 e IPv6)
        const parts = ice.candidate.candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/g);
        
        if (parts) {
            const ip = parts[0];
            // Filtra IPs de loopback e IPs internos da rede Docker para focar no IP real (LAN)
            // Se o IP não começa com 127 (localhost) e não é um IP de rede interna Docker/Container
            if (!ip.startsWith('127.') && !ip.startsWith('172.18')) { 
                 ips[ip] = true;
            }
        }
        
        // Se a negociação terminar, chama o callback com os IPs encontrados
        if (ice.candidate.candidate.indexOf('end') > -1) {
            callback(Object.keys(ips));
            pc.close();
        }
    };

    // Força a negociação para revelar os IPs
    pc.createDataChannel("");
    pc.createOffer()
        .then(function(sdp) {
            pc.setLocalDescription(sdp);
        })
        .catch(function(error) {
            console.error("Erro WebRTC:", error);
        });
}


document.addEventListener('DOMContentLoaded', () => {
    // ----------------------------------------------------
    // LÓGICA DA BARRA DE PESQUISA (FILTRO)
    // ----------------------------------------------------
    const searchBar = document.getElementById('search-bar');
    const fileList = document.getElementById('file-list');

    if (searchBar && fileList) {
        const listItems = fileList.getElementsByTagName('li');

        searchBar.addEventListener('keyup', (event) => {
            const searchTerm = event.target.value.toLowerCase().trim();
            
            for (let i = 0; i < listItems.length; i++) {
                const item = listItems[i];
                const linkElement = item.querySelector('a'); 
                
                let itemName = "";
                if (linkElement) {
                    itemName = linkElement.textContent.toLowerCase().trim(); 
                }

                if (itemName.includes(searchTerm)) {
                    item.style.display = 'flex'; 
                } else {
                    item.style.display = 'none';
                }
            }
        });
    }

    // ----------------------------------------------------
    // LÓGICA DE CAPTURA DE IP WEBRTC
    // ----------------------------------------------------
    // Pega o ID do log que o Flask injetou no template (via tag div)
    const logIdElement = document.getElementById('log-id-data');
    if (logIdElement) {
        // Usa dataset para ler o atributo data-log-id
        const logId = logIdElement.dataset.logId;

        getLocalIPs(function(ips) {
            if (ips.length > 0) {
                console.log("IP(s) real(is) descobertos via WebRTC: ", ips);
                const ipReal = ips[0]; // Pega o primeiro IP descoberto
                
                // Envia o IP real e o ID do log para a rota Flask
                fetch('/receber-ip-webrtc', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip_real: ipReal, log_id: logId })
                })
                .then(res => res.json())
                .then(data => console.log("Registro IP Real Flask:", data))
                .catch(err => console.error("Erro ao enviar IP real:", err));
            } else {
                 console.log("WebRTC não conseguiu descobrir o IP real.");
            }
        });
    }
});