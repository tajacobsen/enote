# Maintainer: Troels Jacobsen <tkjacobsen@gmail.com>
pkgname=enote
pkgver=0.0.1
pkgrel=1
pkgdesc='Command line utility to backup Evernote notes and notebooks'
arch=(any)
url="https://github.com/tkjacobsen/$pkgname"
license=('MIT')
depends=('evernote-sdk-python-git'
         'python2-oauth2'
         'python2-beautifulsoup4'
         'python2-html2text-git')
#makedepends=()
source=("$url/archive/$pkgver.tar.gz")
sha256sums=('d670fbaefeccf8b44fa7cc7311afabef6c0ab2aeb143cf4eb41d1af112fafcd2')

package() {
	cd "$pkgname-$pkgver"
    python2 setup.py install --root="$pkgdir/"
}

