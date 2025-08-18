#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import random
import threading
import subprocess
from typing import List, Dict

class WifiSimTool:
    def __init__(self):
        self.interface = None
        self.running = False
        self.processes = []
        self.ssid_list = []

        self.oui_prefixes = [
            "00:1A:2B", "00:1B:3C", "00:2A:3B", "08:00:27",
            "00:50:56", "00:0C:29", "52:54:00", "02:00:00",
            "00:16:EA", "00:19:DB", "00:1C:BF", "00:21:6A",
            "00:23:6C", "00:24:2B", "00:26:BB", "00:1D:7E"
        ]

    def load_ssids_from_file(self, filename="ssids.txt"):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.ssid_list = [line.strip() for line in f if line.strip()]
                print(f"Carregados {len(self.ssid_list)} SSIDs do arquivo {filename}")
                return True
            else:
                self.create_default_ssids_file(filename)
                return self.load_ssids_from_file(filename)
        except Exception as e:
            print(f"Erro ao carregar arquivo de SSIDs: {e}")
            return False

    def create_default_ssids_file(self, filename):
        default_ssids = [
            "Internet Gratis", "WIFI-CASA", "INTERNET FREE", "Prefeitura",
            "Free WiFi", "Public WiFi", "WiFi Livre", "Rede Aberta",
            "WiFi Casa", "WiFi Escola", "Claro WiFi", "Oi WiFi",
            "Vivo Internet", "NET Virtua", "Internet Rápida", "WiFi Rápido",
            "Rede Livre", "Rede Publica", "WiFi Publico", "NETFREE",
            "WiFi Gratuito", "Rede Aberta 24h", "WiFi 24h", "Wifi Livre",
            "WiFi Open", "Acesso Livre", "FREE-WIFI", "WiFi-Gratis",
            "Internet-Livre", "OPEN-NETWORK", "WIFI", "McDonald's WiFi",
            "Starbucks", "Shopping WiFi", "Hotel WiFi", "Aeroporto WiFi"
        ]

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for ssid in default_ssids:
                    f.write(f"{ssid}\n")
            print(f"Arquivo {filename} criado com SSIDs padrão")
        except Exception as e:
            print(f"Erro ao criar arquivo padrão: {e}")

    def check_dependencies(self):
        tools = ['hostapd', 'airbase-ng', 'iwconfig']
        missing = []

        for tool in tools:
            try:
                subprocess.run(['which', tool], check=True,
                             capture_output=True, text=True)
            except subprocess.CalledProcessError:
                missing.append(tool)

        return len(missing) == 0, missing

    def scan_wireless_interfaces(self):
        try:
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            interfaces = []

            for line in result.stdout.split('\n'):
                if 'IEEE 802.11' in line and line.strip():
                    interface = line.split()[0]
                    interfaces.append(interface)

            return interfaces
        except:
            return []

    def setup_monitor_mode(self, interface):
        commands = [
            ['sudo', 'ifconfig', interface, 'down'],
            ['sudo', 'airmon-ng', 'check', 'kill'],
            ['sudo', 'iwconfig', interface, 'mode', 'monitor'],
            ['sudo', 'ifconfig', interface, 'up']
        ]

        try:
            for cmd in commands:
                subprocess.run(cmd, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def generate_mac_address(self):
        oui = random.choice(self.oui_prefixes)
        suffix = ":".join([f"{random.randint(16,255):02X}" for _ in range(3)])
        return f"{oui}:{suffix}"

    def create_ssid_variations(self, base_count):
        variations = []

        if not self.ssid_list:
            return variations

        base_ssids = random.sample(self.ssid_list,
                                 min(len(self.ssid_list), base_count // 2))
        variations.extend(base_ssids)

        remaining = base_count - len(variations)
        for i in range(remaining):
            base = random.choice(self.ssid_list)
            if random.choice([True, False]):
                variation = f"{base}_{random.randint(1, 99)}"
            else:
                variation = f"{base}-{random.randint(100, 999)}"
            variations.append(variation)

        return variations

    def spawn_fake_ap(self, ssid, channel, mac_addr, use_encryption=False):
        cmd_args = [
            'sudo', 'airbase-ng',
            '-e', ssid,
            '-c', str(channel),
            '-a', mac_addr
        ]

        if use_encryption:
            cmd_args.extend(['-W', '1'])

        cmd_args.append(self.interface)

        return subprocess.Popen(cmd_args, stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

    def start_simulation(self, network_count=30):
        print(f"Iniciando simulação com {network_count} redes WiFi...")
        print("Pressione Ctrl+C para interromper")

        ssids = self.create_ssid_variations(network_count)
        self.running = True

        try:
            for idx, ssid in enumerate(ssids, 1):
                if not self.running:
                    break

                channel = random.randint(1, 11)
                mac = self.generate_mac_address()
                encrypted = random.choice([True, False])

                print(f"[{idx:03d}] {ssid} | Canal: {channel} | MAC: {mac}")

                process = self.spawn_fake_ap(ssid, channel, mac, encrypted)
                self.processes.append(process)

                time.sleep(random.uniform(0.3, 0.7))

            print(f"\n{len(self.processes)} redes ativas!")
            print("Simulação em execução... (Ctrl+C para parar)\n")

            while self.running:
                time.sleep(2)

        except KeyboardInterrupt:
            print("\nInterrompendo simulação...")
            self.cleanup()

    def cleanup(self):
        self.running = False
        print("Finalizando processos...")

        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=2)
            except:
                try:
                    process.kill()
                except:
                    pass

        self.processes.clear()
        print("Processos finalizados!")
        self.restore_network_interface()

    def restore_network_interface(self):
        if self.interface:
            print("Restaurando interface de rede...")
            try:
                restore_commands = [
                    ['sudo', 'ifconfig', self.interface, 'down'],
                    ['sudo', 'iwconfig', self.interface, 'mode', 'managed'],
                    ['sudo', 'ifconfig', self.interface, 'up'],
                    ['sudo', 'systemctl', 'restart', 'NetworkManager']
                ]

                for cmd in restore_commands:
                    subprocess.run(cmd, capture_output=True)

                print("Interface restaurada com sucesso!")

            except Exception as e:
                print(f"Erro na restauração: {e}")
                print("Execute manualmente:")
                print(f"  sudo iwconfig {self.interface} mode managed")
                print("  sudo systemctl restart NetworkManager")

    def interactive_mode(self):
        print("=" * 50)
        print("       WifiSIM-Tool v1.0")
        print("   Simulador de Redes WiFi")
        print("=" * 50)
        print("ATENÇÃO: Para uso educacional apenas!\n")

        deps_ok, missing = self.check_dependencies()
        if not deps_ok:
            print("Dependências não encontradas:")
            for tool in missing:
                print(f"  - {tool}")
            print("\nInstale com: sudo apt install hostapd aircrack-ng")
            return

        if not self.load_ssids_from_file():
            print("Falha ao carregar lista de SSIDs!")
            return

        interfaces = self.scan_wireless_interfaces()
        if not interfaces:
            print("Nenhuma interface wireless encontrada!")
            return

        print("Interfaces disponíveis:")
        for i, iface in enumerate(interfaces, 1):
            print(f"  {i}. {iface}")

        try:
            selection = int(input("\nSelecione a interface: ")) - 1
            self.interface = interfaces[selection]
        except (ValueError, IndexError):
            print("Seleção inválida!")
            return

        try:
            count = input("Número de redes (padrão: 25): ").strip()
            count = int(count) if count else 25
        except ValueError:
            count = 25

        print(f"\nConfigurando {self.interface} em modo monitor...")
        if not self.setup_monitor_mode(self.interface):
            print("Falha ao configurar modo monitor!")
            print("Certifique-se de executar como root")
            return

        print("Modo monitor ativado!")
        time.sleep(1)

        self.start_simulation(count)


def main():
    if os.geteuid() != 0:
        print("Este script requer privilégios de root!")
        print("Execute com: sudo python3 wifisim_tool.py")
        sys.exit(1)

    simulator = WifiSimTool()

    try:
        simulator.interactive_mode()
    except KeyboardInterrupt:
        print("\nPrograma interrompido")
        simulator.cleanup()
    except Exception as e:
        print(f"Erro: {e}")
        simulator.cleanup()


if __name__ == "__main__":
    main()
