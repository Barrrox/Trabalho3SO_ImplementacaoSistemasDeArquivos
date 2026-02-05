# Como puxar o pendrive pelo WSL


1. No windows, instale o usbipd:

```ps
winget install dorssel.usbipd-win
```
OBS: Lembre de abrir um novo terminal para prosseguir

2. Liste os dispositivos: 

```ps
usbipd list
```

3. Identifique o seu pendrive pelo BUSID (ex: 2-1).

4. Compartilhe o dispositivo: 

```ps
usbipd bind --busid <BUSID>
```
5. Execute o WSL em um terminal diferente

6. no terminal do windows, anexe ao WSL: 

```ps
usbipd attach --wsl --busid <BUSID>
```

7. No WSL (Terminal), rode o comando:

```ps
lsblk
```

Agora seu pendrive deve aparecer como "sd<alguma letra>" (Ex: sdb, sde). Use "sd<alguma letra>1"

