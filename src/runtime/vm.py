#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moduł zarządzania maszynami wirtualnymi dla AI Environment Manager.

Implementuje funkcje do tworzenia, uruchamiania, zatrzymywania
i zarządzania maszynami wirtualnymi.
"""

import json
import logging
import os
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml

from ..core.config import CONFIG_DIR, config

logger = logging.getLogger("ai-env-manager.runtime.vm")


class VMRuntime:
    """
    Klasa do zarządzania maszynami wirtualnymi.

    Implementuje funkcje do tworzenia, uruchamiania, zatrzymywania
    i zarządzania maszynami wirtualnymi dla środowisk AI.
    """

    def __init__(self, vm_dir: Optional[Path] = None):
        """
        Inicjalizuje zarządcę maszyn wirtualnych.

        Args:
            vm_dir: Katalog z obrazami VM (opcjonalny)
        """
        self.vm_dir = vm_dir or Path(
            config.get("paths.vm_images", CONFIG_DIR / "vm-images")
        )
        self.vm_dir.mkdir(parents=True, exist_ok=True)

        # Typ hypervisora (kvm, virtualbox)
        self.vm_type = config.get("runtime.vm.type", "kvm")
        self.network = config.get("runtime.vm.network", "default")

        # Sprawdź czy hypervisor jest dostępny
        self.is_available = self._check_availability()
        if not self.is_available:
            logger.warning(f"Hypervisor {self.vm_type} nie jest dostępny w systemie")

        # Słownik uruchomionych maszyn wirtualnych
        self.running_vms = {}
        self._load_running_vms()

    def _check_availability(self) -> bool:
        """
        Sprawdza czy wybrany hypervisor jest dostępny w systemie.

        Returns:
            bool: True jeśli hypervisor jest dostępny
        """
        try:
            if self.vm_type == "kvm":
                # Sprawdź czy KVM jest dostępny
                result = subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "list"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                return result.returncode == 0
            elif self.vm_type == "virtualbox":
                # Sprawdź czy VirtualBox jest dostępny
                result = subprocess.run(
                    ["VBoxManage", "list", "vms"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                return result.returncode == 0
            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return False
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania dostępności hypervisora: {e}")
            return False

    def _load_running_vms(self) -> None:
        """Ładuje informacje o uruchomionych maszynach wirtualnych"""
        try:
            vm_state_file = self.vm_dir / "vm_state.json"
            if vm_state_file.exists():
                with open(vm_state_file, "r", encoding="utf-8") as f:
                    self.running_vms = json.load(f)
                logger.debug(
                    f"Załadowano informacje o {len(self.running_vms)} uruchomionych VM"
                )
        except Exception as e:
            logger.error(f"Błąd podczas ładowania stanu VM: {e}")
            self.running_vms = {}

    def _save_running_vms(self) -> None:
        """Zapisuje informacje o uruchomionych maszynach wirtualnych"""
        try:
            vm_state_file = self.vm_dir / "vm_state.json"
            with open(vm_state_file, "w", encoding="utf-8") as f:
                json.dump(self.running_vms, f, indent=2)
            logger.debug(
                f"Zapisano informacje o {len(self.running_vms)} uruchomionych VM"
            )
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania stanu VM: {e}")

    def list_vms(self) -> List[Dict[str, Any]]:
        """
        Zwraca listę wszystkich dostępnych maszyn wirtualnych.

        Returns:
            List[Dict[str, Any]]: Lista słowników z informacjami o VM
        """
        vms = []

        try:
            if self.vm_type == "kvm":
                # Pobierz listę VM z libvirt
                result = subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "list", "--all", "--name"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                vm_names = [
                    name.strip() for name in result.stdout.splitlines() if name.strip()
                ]

                for name in vm_names:
                    # Sprawdź czy VM jest uruchomiona
                    status_result = subprocess.run(
                        ["virsh", "--connect", "qemu:///system", "domstate", name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                        text=True,
                    )

                    status = (
                        status_result.stdout.strip()
                        if status_result.returncode == 0
                        else "unknown"
                    )

                    # Pobierz informacje o VM
                    vm_info = {
                        "name": name,
                        "status": status,
                        "type": "kvm",
                        "id": name,
                        "metadata": self.running_vms.get(name, {}),
                    }

                    vms.append(vm_info)

            elif self.vm_type == "virtualbox":
                # Pobierz listę VM z VirtualBox
                result = subprocess.run(
                    ["VBoxManage", "list", "vms"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                for line in result.stdout.splitlines():
                    if not line.strip():
                        continue

                    # Format: "VM Name" {uuid}
                    parts = line.split('" {')
                    if len(parts) != 2:
                        continue

                    name = parts[0].strip('"')
                    vm_id = "{" + parts[1].strip()

                    # Sprawdź status VM
                    status_result = subprocess.run(
                        ["VBoxManage", "showvminfo", "--machinereadable", name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=False,
                        text=True,
                    )

                    status = "stopped"
                    if status_result.returncode == 0:
                        for status_line in status_result.stdout.splitlines():
                            if status_line.startswith("VMState="):
                                vm_state = status_line.split("=")[1].strip('"')
                                status = (
                                    "running" if vm_state == "running" else "stopped"
                                )
                                break

                    # Pobierz informacje o VM
                    vm_info = {
                        "name": name,
                        "status": status,
                        "type": "virtualbox",
                        "id": vm_id,
                        "metadata": self.running_vms.get(name, {}),
                    }

                    vms.append(vm_info)
        except Exception as e:
            logger.error(f"Błąd podczas pobierania listy VM: {e}")

        return vms

    def create_vm(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Tworzy nową maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            config: Konfiguracja maszyny wirtualnej
                - image: Ścieżka do obrazu bazowego
                - memory: Ilość pamięci RAM (MB)
                - cpu: Liczba rdzeni CPU
                - disk: Rozmiar dysku (GB)
                - network: Konfiguracja sieci

        Returns:
            bool: True jeśli utworzenie VM się powiodło
        """
        if not self.is_available:
            logger.error(f"Hypervisor {self.vm_type} nie jest dostępny")
            return False

        try:
            # Pobierz parametry konfiguracji
            image_path = config.get("image")
            memory = config.get("memory", 2048)  # MB
            cpu_cores = config.get("cpu", 2)
            disk_size = config.get("disk", 20)  # GB
            network_config = config.get("network", {"type": "default"})

            if not image_path:
                logger.error("Nie podano ścieżki do obrazu bazowego")
                return False

            # Utwórz katalog dla VM
            vm_path = self.vm_dir / name
            vm_path.mkdir(exist_ok=True)

            if self.vm_type == "kvm":
                # Utwórz kopię obrazu bazowego
                disk_path = vm_path / f"{name}.qcow2"

                # Utwórz obraz dysku
                subprocess.run(
                    [
                        "qemu-img",
                        "create",
                        "-f",
                        "qcow2",
                        "-b",
                        image_path,
                        disk_path,
                        f"{disk_size}G",
                    ],
                    check=True,
                )

                # Utwórz plik XML z definicją VM
                xml_path = vm_path / f"{name}.xml"

                # Podstawowy szablon XML dla KVM
                xml_template = f"""
                <domain type='kvm'>
                  <name>{name}</name>
                  <uuid>{uuid.uuid4()}</uuid>
                  <memory unit='MiB'>{memory}</memory>
                  <vcpu>{cpu_cores}</vcpu>
                  <os>
                    <type arch='x86_64'>hvm</type>
                    <boot dev='hd'/>
                  </os>
                  <features>
                    <acpi/>
                    <apic/>
                  </features>
                  <devices>
                    <disk type='file' device='disk'>
                      <driver name='qemu' type='qcow2'/>
                      <source file='{disk_path}'/>
                      <target dev='vda' bus='virtio'/>
                    </disk>
                    <interface type='network'>
                      <source network='{self.network}'/>
                      <model type='virtio'/>
                    </interface>
                    <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
                      <listen type='address' address='0.0.0.0'/>
                    </graphics>
                    <console type='pty'/>
                  </devices>
                </domain>
                """

                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(xml_template.strip())

                # Zdefiniuj VM w libvirt
                subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "define", xml_path],
                    check=True,
                )

                logger.info(f"Utworzono maszynę wirtualną KVM: {name}")
                return True

            elif self.vm_type == "virtualbox":
                # Utwórz VM w VirtualBox
                subprocess.run(
                    ["VBoxManage", "createvm", "--name", name, "--register"], check=True
                )

                # Ustaw parametry VM
                subprocess.run(
                    [
                        "VBoxManage",
                        "modifyvm",
                        name,
                        "--memory",
                        str(memory),
                        "--cpus",
                        str(cpu_cores),
                    ],
                    check=True,
                )

                # Utwórz dysk
                disk_path = vm_path / f"{name}.vdi"
                subprocess.run(
                    [
                        "VBoxManage",
                        "createhd",
                        "--filename",
                        disk_path,
                        "--size",
                        str(disk_size * 1024),
                    ],
                    check=True,
                )

                # Dodaj kontroler SATA
                subprocess.run(
                    [
                        "VBoxManage",
                        "storagectl",
                        name,
                        "--name",
                        "SATA",
                        "--add",
                        "sata",
                        "--controller",
                        "IntelAHCI",
                    ],
                    check=True,
                )

                # Podłącz dysk
                subprocess.run(
                    [
                        "VBoxManage",
                        "storageattach",
                        name,
                        "--storagectl",
                        "SATA",
                        "--port",
                        "0",
                        "--device",
                        "0",
                        "--type",
                        "hdd",
                        "--medium",
                        disk_path,
                    ],
                    check=True,
                )

                # Skonfiguruj sieć
                network_type = network_config.get("type", "nat")
                subprocess.run(
                    ["VBoxManage", "modifyvm", name, "--nic1", network_type], check=True
                )

                logger.info(f"Utworzono maszynę wirtualną VirtualBox: {name}")
                return True

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return False

        except Exception as e:
            logger.error(f"Błąd podczas tworzenia VM {name}: {e}")
            return False

    def start_vm(self, name: str) -> bool:
        """
        Uruchamia maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            bool: True jeśli uruchomienie VM się powiodło
        """
        if not self.is_available:
            logger.error(f"Hypervisor {self.vm_type} nie jest dostępny")
            return False

        try:
            if self.vm_type == "kvm":
                # Uruchom VM w libvirt
                subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "start", name], check=True
                )

                # Pobierz adres IP (może nie być od razu dostępny)
                ip_address = self._get_vm_ip(name)

                # Zapisz informacje o uruchomionej VM
                self.running_vms[name] = {
                    "status": "running",
                    "ip": ip_address,
                    "started_at": str(datetime.now().isoformat()),
                }
                self._save_running_vms()

                logger.info(f"Uruchomiono maszynę wirtualną KVM: {name}")
                return True

            elif self.vm_type == "virtualbox":
                # Uruchom VM w VirtualBox
                subprocess.run(
                    ["VBoxManage", "startvm", name, "--type", "headless"], check=True
                )

                # Pobierz adres IP (może nie być od razu dostępny)
                ip_address = self._get_vm_ip(name)

                # Zapisz informacje o uruchomionej VM
                self.running_vms[name] = {
                    "status": "running",
                    "ip": ip_address,
                    "started_at": str(datetime.now().isoformat()),
                }
                self._save_running_vms()

                logger.info(f"Uruchomiono maszynę wirtualną VirtualBox: {name}")
                return True

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return False

        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania VM {name}: {e}")
            return False

    def stop_vm(self, name: str, force: bool = False) -> bool:
        """
        Zatrzymuje maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej
            force: Czy wymusić zatrzymanie (odpowiednik wyłączenia zasilania)

        Returns:
            bool: True jeśli zatrzymanie VM się powiodło
        """
        if not self.is_available:
            logger.error(f"Hypervisor {self.vm_type} nie jest dostępny")
            return False

        try:
            if self.vm_type == "kvm":
                if force:
                    # Wymuś zatrzymanie VM
                    subprocess.run(
                        ["virsh", "--connect", "qemu:///system", "destroy", name],
                        check=True,
                    )
                else:
                    # Zatrzymaj VM "grzecznie"
                    subprocess.run(
                        ["virsh", "--connect", "qemu:///system", "shutdown", name],
                        check=True,
                    )

                # Usuń informacje o uruchomionej VM
                if name in self.running_vms:
                    del self.running_vms[name]
                    self._save_running_vms()

                logger.info(f"Zatrzymano maszynę wirtualną KVM: {name}")
                return True

            elif self.vm_type == "virtualbox":
                if force:
                    # Wymuś zatrzymanie VM
                    subprocess.run(
                        ["VBoxManage", "controlvm", name, "poweroff"], check=True
                    )
                else:
                    # Zatrzymaj VM "grzecznie"
                    subprocess.run(
                        ["VBoxManage", "controlvm", name, "acpipowerbutton"], check=True
                    )

                # Usuń informacje o uruchomionej VM
                if name in self.running_vms:
                    del self.running_vms[name]
                    self._save_running_vms()

                logger.info(f"Zatrzymano maszynę wirtualną VirtualBox: {name}")
                return True

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return False

        except Exception as e:
            logger.error(f"Błąd podczas zatrzymywania VM {name}: {e}")
            return False

    def delete_vm(self, name: str) -> bool:
        """
        Usuwa maszynę wirtualną.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            bool: True jeśli usunięcie VM się powiodło
        """
        if not self.is_available:
            logger.error(f"Hypervisor {self.vm_type} nie jest dostępny")
            return False

        try:
            # Najpierw zatrzymaj VM jeśli jest uruchomiona
            vm_list = self.list_vms()
            for vm in vm_list:
                if vm["name"] == name and vm["status"] == "running":
                    self.stop_vm(name, force=True)
                    break

            if self.vm_type == "kvm":
                # Usuń definicję VM z libvirt
                subprocess.run(
                    [
                        "virsh",
                        "--connect",
                        "qemu:///system",
                        "undefine",
                        name,
                        "--remove-all-storage",
                    ],
                    check=True,
                )

                # Usuń katalog VM
                vm_path = self.vm_dir / name
                if vm_path.exists():
                    shutil.rmtree(vm_path)

                # Usuń informacje o VM
                if name in self.running_vms:
                    del self.running_vms[name]
                    self._save_running_vms()

                logger.info(f"Usunięto maszynę wirtualną KVM: {name}")
                return True

            elif self.vm_type == "virtualbox":
                # Usuń VM z VirtualBox
                subprocess.run(
                    ["VBoxManage", "unregistervm", name, "--delete"], check=True
                )

                # Usuń katalog VM
                vm_path = self.vm_dir / name
                if vm_path.exists():
                    shutil.rmtree(vm_path)

                # Usuń informacje o VM
                if name in self.running_vms:
                    del self.running_vms[name]
                    self._save_running_vms()

                logger.info(f"Usunięto maszynę wirtualną VirtualBox: {name}")
                return True

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return False

        except Exception as e:
            logger.error(f"Błąd podczas usuwania VM {name}: {e}")
            return False

    def _get_vm_ip(self, name: str) -> Optional[str]:
        """
        Pobiera adres IP maszyny wirtualnej.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Optional[str]: Adres IP lub None jeśli nie znaleziono
        """
        try:
            if self.vm_type == "kvm":
                # Pobierz adres MAC interfejsu sieciowego VM
                mac_result = subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "domiflist", name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                mac_address = None
                for line in mac_result.stdout.splitlines():
                    if self.network in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            mac_address = parts[4]
                            break

                if not mac_address:
                    return None

                # Pobierz adres IP na podstawie adresu MAC
                ip_result = subprocess.run(
                    [
                        "virsh",
                        "--connect",
                        "qemu:///system",
                        "net-dhcp-leases",
                        self.network,
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                for line in ip_result.stdout.splitlines():
                    if mac_address in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            return parts[4].split("/")[0]

                return None

            elif self.vm_type == "virtualbox":
                # Pobierz informacje o VM
                info_result = subprocess.run(
                    ["VBoxManage", "guestproperty", "enumerate", name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                for line in info_result.stdout.splitlines():
                    if "/VirtualBox/GuestInfo/Net/0/V4/IP" in line:
                        parts = line.split(", ")
                        if len(parts) >= 2:
                            return parts[1].split(": ")[1]

                return None

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return None

        except Exception as e:
            logger.error(f"Błąd podczas pobierania adresu IP VM {name}: {e}")
            return None

    def get_vm_status(self, name: str) -> Dict[str, Any]:
        """
        Pobiera status maszyny wirtualnej.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Dict[str, Any]: Słownik z informacjami o statusie VM
        """
        vm_list = self.list_vms()
        for vm in vm_list:
            if vm["name"] == name:
                return vm

        return {
            "name": name,
            "status": "not_found",
            "type": self.vm_type,
            "id": "",
            "metadata": {},
        }

    def get_vm_console_url(self, name: str) -> Optional[str]:
        """
        Pobiera URL do konsoli maszyny wirtualnej.

        Args:
            name: Nazwa maszyny wirtualnej

        Returns:
            Optional[str]: URL do konsoli VM lub None jeśli nie znaleziono
        """
        try:
            if self.vm_type == "kvm":
                # Pobierz port VNC dla VM
                result = subprocess.run(
                    ["virsh", "--connect", "qemu:///system", "vncdisplay", name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                vnc_port = result.stdout.strip()
                if vnc_port:
                    # Konwertuj na numer portu (np. :0 -> 5900)
                    port = 5900 + int(vnc_port.replace(":", ""))
                    return f"vnc://localhost:{port}"

                return None

            elif self.vm_type == "virtualbox":
                # VirtualBox nie udostępnia bezpośrednio URL do konsoli
                # Można użyć VRDE (VirtualBox Remote Desktop Extension)
                result = subprocess.run(
                    ["VBoxManage", "showvminfo", name, "--machinereadable"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                    text=True,
                )

                vrde_enabled = False
                vrde_port = None

                for line in result.stdout.splitlines():
                    if line.startswith("vrde="):
                        vrde_enabled = line.split("=")[1].strip('"') == "on"
                    elif line.startswith("vrdeport="):
                        vrde_port = line.split("=")[1].strip('"')

                if vrde_enabled and vrde_port:
                    return f"rdp://localhost:{vrde_port}"

                return None

            else:
                logger.error(f"Nieobsługiwany typ hypervisora: {self.vm_type}")
                return None

        except Exception as e:
            logger.error(f"Błąd podczas pobierania URL konsoli VM {name}: {e}")
            return None
