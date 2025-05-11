#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Przykład użycia API twinshare do zarządzania maszynami wirtualnymi i siecią P2P.
"""

import asyncio
import json
from src.api import API

# Inicjalizacja głównego API
api = API()


async def vm_management_example():
    """Przykład zarządzania maszynami wirtualnymi."""
    print("=== Przykład zarządzania maszynami wirtualnymi ===")
    
    # Listowanie maszyn wirtualnych
    print("\n1. Listowanie maszyn wirtualnych:")
    vms = api.vm.list_vms()
    print(json.dumps(vms, indent=2))
    
    # Tworzenie maszyny wirtualnej
    print("\n2. Tworzenie maszyny wirtualnej:")
    try:
        vm = api.vm.create_vm(
            name="example-vm",
            image="ubuntu-20.04",
            cpu_cores=2,
            memory=2048,
            disk_size=20
        )
        print(json.dumps(vm, indent=2))
    except Exception as e:
        print(f"Błąd podczas tworzenia maszyny wirtualnej: {e}")
    
    # Pobieranie statusu maszyny wirtualnej
    print("\n3. Pobieranie statusu maszyny wirtualnej:")
    try:
        status = api.vm.get_vm_status("example-vm")
        print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Błąd podczas pobierania statusu maszyny wirtualnej: {e}")
    
    # Uruchamianie maszyny wirtualnej
    print("\n4. Uruchamianie maszyny wirtualnej:")
    try:
        api.vm.start_vm("example-vm")
        print("Maszyna wirtualna została uruchomiona.")
    except Exception as e:
        print(f"Błąd podczas uruchamiania maszyny wirtualnej: {e}")
    
    # Zatrzymywanie maszyny wirtualnej
    print("\n5. Zatrzymywanie maszyny wirtualnej:")
    try:
        api.vm.stop_vm("example-vm")
        print("Maszyna wirtualna została zatrzymana.")
    except Exception as e:
        print(f"Błąd podczas zatrzymywania maszyny wirtualnej: {e}")
    
    # Usuwanie maszyny wirtualnej
    print("\n6. Usuwanie maszyny wirtualnej:")
    try:
        api.vm.delete_vm("example-vm")
        print("Maszyna wirtualna została usunięta.")
    except Exception as e:
        print(f"Błąd podczas usuwania maszyny wirtualnej: {e}")


async def p2p_example():
    """Przykład zarządzania siecią P2P."""
    print("\n=== Przykład zarządzania siecią P2P ===")
    
    # Uruchamianie usług P2P
    print("\n1. Uruchamianie usług P2P:")
    await api.p2p.start_services()
    print("Usługi P2P zostały uruchomione.")
    
    # Pobieranie informacji o lokalnym węźle
    print("\n2. Pobieranie informacji o lokalnym węźle:")
    local_info = api.p2p.get_local_peer_info()
    print(json.dumps(local_info, indent=2))
    
    # Listowanie węzłów w sieci
    print("\n3. Listowanie węzłów w sieci:")
    peers = api.p2p.get_peers()
    print(json.dumps(peers, indent=2))
    
    # Jeśli są dostępne węzły, wyślij wiadomość do pierwszego z nich
    if peers:
        peer_id = peers[0].get("id")
        print(f"\n4. Wysyłanie wiadomości do węzła {peer_id}:")
        try:
            response = await api.p2p.send_message(
                peer_id=peer_id,
                message_type="HELLO",
                data={"message": "Hello from API example!"}
            )
            print("Odpowiedź:")
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Błąd podczas wysyłania wiadomości: {e}")
    
    # Zatrzymywanie usług P2P
    print("\n5. Zatrzymywanie usług P2P:")
    await api.p2p.stop_services()
    print("Usługi P2P zostały zatrzymane.")


async def remote_vm_example():
    """Przykład zdalnego zarządzania maszynami wirtualnymi."""
    print("\n=== Przykład zdalnego zarządzania maszynami wirtualnymi ===")
    
    # Uruchamianie usług P2P
    await api.p2p.start_services()
    
    # Listowanie węzłów w sieci
    peers = api.p2p.get_peers()
    
    if not peers:
        print("Brak dostępnych węzłów w sieci.")
        await api.p2p.stop_services()
        return
    
    peer_id = peers[0].get("id")
    print(f"Używanie węzła: {peer_id}")
    
    # Listowanie zdalnych maszyn wirtualnych
    print("\n1. Listowanie zdalnych maszyn wirtualnych:")
    try:
        remote_vms = await api.vm.list_remote_vms(peer_id)
        print(json.dumps(remote_vms, indent=2))
    except Exception as e:
        print(f"Błąd podczas listowania zdalnych maszyn wirtualnych: {e}")
    
    # Tworzenie zdalnej maszyny wirtualnej
    print("\n2. Tworzenie zdalnej maszyny wirtualnej:")
    try:
        response = await api.vm.create_remote_vm(
            peer_id=peer_id,
            name="remote-example-vm",
            image="ubuntu-20.04",
            cpu_cores=2,
            memory=2048,
            disk_size=20
        )
        print(json.dumps(response, indent=2))
        
        # Pobierz ID utworzonej maszyny wirtualnej
        vm_id = response.get("vm_id", "remote-example-vm")
        
        # Uruchamianie zdalnej maszyny wirtualnej
        print("\n3. Uruchamianie zdalnej maszyny wirtualnej:")
        response = await api.vm.start_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
        # Zatrzymywanie zdalnej maszyny wirtualnej
        print("\n4. Zatrzymywanie zdalnej maszyny wirtualnej:")
        response = await api.vm.stop_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
        # Usuwanie zdalnej maszyny wirtualnej
        print("\n5. Usuwanie zdalnej maszyny wirtualnej:")
        response = await api.vm.delete_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"Błąd podczas operacji na zdalnej maszynie wirtualnej: {e}")
    
    # Zatrzymywanie usług P2P
    await api.p2p.stop_services()


async def main():
    """Główna funkcja przykładowa."""
    print("twinshare API - Przykłady użycia")
    print("================================\n")
    
    # Przykład zarządzania maszynami wirtualnymi
    await vm_management_example()
    
    # Przykład zarządzania siecią P2P
    await p2p_example()
    
    # Przykład zdalnego zarządzania maszynami wirtualnymi
    await remote_vm_example()


if __name__ == "__main__":
    asyncio.run(main())
