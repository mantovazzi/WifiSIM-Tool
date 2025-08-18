# WifiSIM-Tool

Um simulador de redes WiFi para fins educacionais e testes de segurança.

## 🎯 Propósito

O WifiSIM-Tool cria múltiplas redes WiFi virtuais para simular ambientes complexos de rede sem fio. Ideal para:

- Testes de penetração

## ⚠️ Aviso Legal

O uso inadequado ou malicioso desta ferramenta é de total responsabilidade do usuário. Use apenas em redes próprias ou com permissão explícita.

## 🛠️ Requisitos

### Sistema Operacional
- Linux (testado em Ubuntu/Debian)
- Privilégios de root

### Dependências
```bash
sudo apt update
sudo apt install hostapd aircrack-ng wireless-tools
```

### Hardware
- Interface de rede wireless compatível com modo monitor
- Adaptador WiFi USB recomendado para melhor compatibilidade

## 📥 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/mantovazzi/WifiSIM-Tool.git
cd WifiSIM-Tool
```

2. Torne o script executável:
```bash
chmod +x wifisim.py
```

3. Execute com privilégios de root:
```bash
sudo python3 wifisim.py
```

### Personalização de SSIDs

O programa carrega os nomes das redes WiFi do arquivo `ssids.txt`. Você pode:

- Editar o arquivo `ssids.txt` para adicionar seus próprios SSIDs
- Um SSID por linha
- Suporte a caracteres especiais e acentos
- O programa cria variações automáticas dos SSIDs base

Exemplo de `ssids.txt`:
```
Internet Gratis
WiFi Livre
Free WiFi
Rodoviaria WIFI
McDonald's WiFi
```

## 🛑 Interrompendo a Simulação

Para parar a simulação:
- Pressione `Ctrl+C`

## 🔍 Solução de Problemas

### Erro: "Este script requer privilégios de root"
```bash
sudo python3 wifisim_tool.py
```

### Erro: "Dependências não encontradas"
```bash
sudo apt install hostapd aircrack-ng wireless-tools
```

### Interface não volta ao normal
Execute manualmente:
```bash
sudo iwconfig wlan0 mode managed
sudo systemctl restart NetworkManager
```

## 📄 Licença

Este projeto é disponibilizado sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## ⚖️ Responsabilidade

O desenvolvedor não se responsabiliza pelo uso indevido desta ferramenta. Use com responsabilidade e sempre respeitando as leis locais e os direitos de terceiros.

---

**WifiSIM-Tool v1.0** - Ferramenta para simulação de redes wireless
