import streamlit as st
import subprocess
import os
import signal

st.title('Python Package Manager')

# Benutzerdefiniertes CSS für kleinere Schriftgröße, Trennlinien und Anpassung der Spaltenbreite
st.markdown(
    """
    <style>
    .small-font {
        font-size: 10px !important;
    }

    .output-box {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .conflict {
        color: red;
    }
    
    .btn {
        background-color: #f0f0f0;
        border: none;
        color: black;
        padding: 5px 10px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 12px;
        margin: 2px 1px;
        cursor: pointer;
        border-radius: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Funktion zur Anzeige installierter Pakete
def get_installed_packages():
    result = subprocess.run(['pip', 'list', '--format=columns'], stdout=subprocess.PIPE)
    package_list = result.stdout.decode('utf-8').split('\n')[2:]  # Überspringe die Kopfzeile
    packages = [(pkg.split()[0], pkg.split()[1]) for pkg in package_list if pkg]
    return packages

# Funktion zur Anzeige veralteter Pakete
def get_outdated_packages():
    result = subprocess.run(['pip', 'list', '--outdated', '--format=columns'], stdout=subprocess.PIPE)
    package_list = result.stdout.decode('utf-8').split('\n')[2:]  # Überspringe die Kopfzeile
    packages = [(pkg.split()[0], pkg.split()[1], pkg.split()[2]) for pkg in package_list if pkg]
    return packages

# Funktion zur Überprüfung von Versionskonflikten
def check_for_conflicts():
    result = subprocess.run(['pip', 'check'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8') + result.stderr.decode('utf-8')
    conflicts = [line for line in output.split('\n') if 'requires' in line and 'but none is installed' in line or 'but' in line and 'is installed' in line]
    return output, conflicts

# Funktion zur Installation eines Pakets
def install_package(package_name):
    subprocess.run(['pip', 'install', package_name])

# Funktion zur Deinstallation eines Pakets
def remove_package(package_name):
    subprocess.run(['pip', 'uninstall', '-y', package_name])

# Funktion zum Aktualisieren eines Pakets
def update_package(package_name):
    subprocess.run(['pip', 'install', '--upgrade', package_name])

# Funktion zum Beenden der Anwendung
def close_app():
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)

# Initialisiere den Session State, um den Status der Erfolgsmeldungen zu speichern
if 'update_success' not in st.session_state:
    st.session_state.update_success = {}
if 'remove_success' not in st.session_state:
    st.session_state.remove_success = {}

# Button zum Beenden der Anwendung
if st.button('Close Application'):
    close_app()

# Anzeige der Erfolgsmeldungen für Updates
for package, message in st.session_state.update_success.items():
    st.success(message)

# Anzeige installierter Pakete mit Konfliktüberprüfung
st.header('Installed Packages')
installed_packages = get_installed_packages()
check_output, conflicts = check_for_conflicts()
outdated_packages = get_outdated_packages()

if installed_packages:
    conflict_packages = {conflict.split()[0] for conflict in conflicts}  # Extrahiere Paketnamen aus den Konflikten
    remove_buttons = []
    for package, version in installed_packages:
        package_url = f"https://pypi.org/project/{package}/"
        conflict_message = ', '.join([conflict for conflict in conflicts if conflict.startswith(package)])
        line_class = 'line small-font conflict' if package in conflict_packages else 'line small-font'

        col1, col2, col3, col4 = st.columns([4, 2, 5, 2])
        with col1:
            st.markdown(f'<a href="{package_url}" target="_blank">{package}</a>', unsafe_allow_html=True)
        with col2:
            st.markdown(version)
        with col3:
            st.markdown(conflict_message)
        with col4:
            if st.button('Remove', key=f'remove_{package}'):
                remove_buttons.append(package)

    # Entfernungen nach der Schleife behandeln, um zu vermeiden, dass der Sitzungsstatus mitten im Rendering geändert wird
    for package in remove_buttons:
        remove_package(package)
        st.rerun()

# Ausgabe der Konflikte von pip check
if conflicts:
    st.header('Dependency Conflicts')
    st.markdown(f"<div class='output-box conflict'>{check_output}</div>", unsafe_allow_html=True)
else:
    st.write('No dependency conflicts found.')

# Anzeige veralteter Pakete
st.header('Outdated Packages')
if outdated_packages:
    for package, version, latest_version in outdated_packages:
        if st.session_state.get(f'update_{package}'):
            update_package(package)
            st.session_state.update_success[package] = f'{package} updated to version {latest_version}'
            del st.session_state[f'update_{package}']
            st.rerun()
        
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        with col1:
            st.markdown(package)
        with col2:
            st.markdown(version)
        with col3:
            st.markdown(latest_version)
        with col4:
            if st.button('Update', key=f'update_{package}'):
                st.session_state[f'update_{package}'] = True
                st.rerun()
else:
    st.write('No outdated packages found.')

# Paketinstallation
st.header('Install a New Package')
package_name = st.text_input('Package Name')

if st.button('Install Package'):
    install_package(package_name)
    st.success(f'Package {package_name} installed!')