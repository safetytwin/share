#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Przykład użycia REST API twinshare do zarządzania maszynami wirtualnymi i siecią P2P.
"""

import asyncio
import json
import sys
from pathlib import Path

# Dodaj katalog nadrzędny do ścieżki, aby umożliwić importowanie modułów
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api.rest_client import RESTClient


async def vm_management_example(client):
    """Przykład zarządzania maszynami wirtualnymi przez REST API."""
    print("=== Przykład zarządzania maszynami wirtualnymi przez REST API ===")
    
    # Listowanie maszyn wirtualnych
    print("\n1. Listowanie maszyn wirtualnych:")
    try:
        vms = await client.list_vms()
        print(json.dumps(vms, indent=2))
    except Exception as e:
        print(f"Błąd podczas listowania maszyn wirtualnych: {e}")
    
    # Tworzenie maszyny wirtualnej
    print("\n2. Tworzenie maszyny wirtualnej:")
    try:
        vm = await client.create_vm(
            name="rest-example-vm",
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
        status = await client.get_vm_status("rest-example-vm")
        print(json.dumps(status, indent=2))
    except Exception as e:
        print(f"Błąd podczas pobierania statusu maszyny wirtualnej: {e}")
    
    # Uruchamianie maszyny wirtualnej
    print("\n4. Uruchamianie maszyny wirtualnej:")
    try:
        result = await client.start_vm("rest-example-vm")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Błąd podczas uruchamiania maszyny wirtualnej: {e}")
    
    # Zatrzymywanie maszyny wirtualnej
    print("\n5. Zatrzymywanie maszyny wirtualnej:")
    try:
        result = await client.stop_vm("rest-example-vm")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Błąd podczas zatrzymywania maszyny wirtualnej: {e}")
    
    # Usuwanie maszyny wirtualnej
    print("\n6. Usuwanie maszyny wirtualnej:")
    try:
        result = await client.delete_vm("rest-example-vm")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Błąd podczas usuwania maszyny wirtualnej: {e}")


async def p2p_example(client):
    """Przykład zarządzania siecią P2P przez REST API."""
    print("\n=== Przykład zarządzania siecią P2P przez REST API ===")
    
    # Uruchamianie usług P2P
    print("\n1. Uruchamianie usług P2P:")
    try:
        result = await client.start_p2p_services()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Błąd podczas uruchamiania usług P2P: {e}")
    
    # Pobieranie informacji o lokalnym węźle
    print("\n2. Pobieranie informacji o lokalnym węźle:")
    try:
        info = await client.get_local_peer_info()
        print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o lokalnym węźle: {e}")
    
    # Listowanie węzłów w sieci
    print("\n3. Listowanie węzłów w sieci:")
    try:
        peers = await client.get_peers()
        print(json.dumps(peers, indent=2))
    except Exception as e:
        print(f"Błąd podczas listowania węzłów w sieci: {e}")
    
    # Jeśli są dostępne węzły, wyślij wiadomość do pierwszego z nich
    if peers:
        peer_id = peers[0].get("id")
        print(f"\n4. Wysyłanie wiadomości do węzła {peer_id}:")
        try:
            response = await client.send_message(
                peer_id=peer_id,
                message_type="HELLO",
                data={"message": "Hello from REST API example!"}
            )
            print(json.dumps(response, indent=2))
        except Exception as e:
            print(f"Błąd podczas wysyłania wiadomości: {e}")
    
    # Zatrzymywanie usług P2P
    print("\n5. Zatrzymywanie usług P2P:")
    try:
        result = await client.stop_p2p_services()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Błąd podczas zatrzymywania usług P2P: {e}")


async def remote_vm_example(client):
    """Przykład zdalnego zarządzania maszynami wirtualnymi przez REST API."""
    print("\n=== Przykład zdalnego zarządzania maszynami wirtualnymi przez REST API ===")
    
    # Uruchamianie usług P2P
    try:
        await client.start_p2p_services()
    except Exception as e:
        print(f"Błąd podczas uruchamiania usług P2P: {e}")
        return
    
    # Listowanie węzłów w sieci
    peers = await client.get_peers()
    
    if not peers:
        print("Brak dostępnych węzłów w sieci.")
        await client.stop_p2p_services()
        return
    
    peer_id = peers[0].get("id")
    print(f"Używanie węzła: {peer_id}")
    
    # Listowanie zdalnych maszyn wirtualnych
    print("\n1. Listowanie zdalnych maszyn wirtualnych:")
    try:
        remote_vms = await client.list_remote_vms(peer_id)
        print(json.dumps(remote_vms, indent=2))
    except Exception as e:
        print(f"Błąd podczas listowania zdalnych maszyn wirtualnych: {e}")
    
    # Tworzenie zdalnej maszyny wirtualnej
    print("\n2. Tworzenie zdalnej maszyny wirtualnej:")
    try:
        response = await client.create_remote_vm(
            peer_id=peer_id,
            name="remote-rest-example-vm",
            image="ubuntu-20.04",
            cpu_cores=2,
            memory=2048,
            disk_size=20
        )
        print(json.dumps(response, indent=2))
        
        # Pobierz ID utworzonej maszyny wirtualnej
        vm_id = response.get("vm_id", "remote-rest-example-vm")
        
        # Uruchamianie zdalnej maszyny wirtualnej
        print("\n3. Uruchamianie zdalnej maszyny wirtualnej:")
        response = await client.start_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
        # Zatrzymywanie zdalnej maszyny wirtualnej
        print("\n4. Zatrzymywanie zdalnej maszyny wirtualnej:")
        response = await client.stop_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
        # Usuwanie zdalnej maszyny wirtualnej
        print("\n5. Usuwanie zdalnej maszyny wirtualnej:")
        response = await client.delete_remote_vm(peer_id, vm_id)
        print(json.dumps(response, indent=2))
        
    except Exception as e:
        print(f"Błąd podczas operacji na zdalnej maszynie wirtualnej: {e}")
    
    # Zatrzymywanie usług P2P
    try:
        await client.stop_p2p_services()
    except Exception as e:
        print(f"Błąd podczas zatrzymywania usług P2P: {e}")


async def main():
    """Główna funkcja przykładowa."""
    print("twinshare REST API - Przykłady użycia")
    print("======================================\n")
    
    # Utwórz klienta REST API
    async with RESTClient("http://localhost:8080") as client:
        # Przykład zarządzania maszynami wirtualnymi
        await vm_management_example(client)
        
        # Przykład zarządzania siecią P2P
        await p2p_example(client)
        
        # Przykład zdalnego zarządzania maszynami wirtualnymi
        await remote_vm_example(client)


if __name__ == "__main__":
    asyncio.run(main())
