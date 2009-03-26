# RH 2.2.4-20, SuSE 2.3.1-32
%define name		%{cross_prefix}glibc

# <epoch>:<version>-<release> tags for glibc main package
%define glibccvsversion	2.9
%define glibcversion	2.9
%define __glibcrelease	3
%define glibcepoch	6

# CVS snapshots of glibc
%define RELEASE		0
%if %{RELEASE}
%define source_package	glibc-%{glibcversion}
%define source_dir	glibc-%{glibcversion}
%define _glibcrelease	%{__glibcrelease}
%else
%define snapshot	20081113
%define source_package	glibc-%{glibccvsversion}-%{snapshot}
%define source_dir	glibc-%{glibccvsversion}
%define _glibcrelease	0.%{snapshot}.%{__glibcrelease}
%endif

%if "%{?manbo_mkrel:has_manbo}" == "has_manbo"
%define glibcrelease	%manbo_mkrel %{_glibcrelease}
%else
%define glibcrelease	%mkrel %{_glibcrelease}
%endif

# crypt blowfish support
%define crypt_bf_ver	1.0.2

# Define "cross" to an architecture to which glibc is to be
# cross-compiled
%define build_cross		0
%{expand: %{?cross:		%%global build_cross 1}}

%if %{build_cross}
%define target_cpu	%{cross}
%define cross_prefix	cross-%{target_cpu}-
%define _prefix		/usr/%{target_cpu}-linux
%define _lib		lib
%define _slibdir	%{_prefix}/%{_lib}
%define _slibdir32	%{_prefix}/lib
%else
%define target_cpu	%{_target_cpu}
%define cross_prefix	%{nil}
%define _slibdir	/%{_lib}
%define _slibdir32	/lib
%endif

# Define target (base) architecture
%define arch		%(echo %{target_cpu}|sed -e "s/\\(i.86\\|athlon\\)/i386/" -e "s/amd64/x86_64/" -e "s/\\(sun4.*\\|sparcv[89]\\)/sparc/")
%define isarch()	%(case " %* " in (*" %{arch} "*) echo 1;; (*) echo 0;; esac)

# Define Xen arches to build with -mno-tls-direct-direct-seg-refs
%define xenarches	%{ix86} x86_64

# Define to build nscd with selinux support
%define build_selinux	0

# Flag for build_pdf_doc:
# 1	build glibc with PDF documentation
# 0	don't build PDF glibc documentation (e.g. for bootstrap build)
%define build_pdf_doc	1

# Enable checking by default for arches where we know tests all pass
%define build_check	1

# Allow make check to fail only when running kernels where we know
# tests must pass (no missing features or bugs in the kernel)
%define check_min_kver 2.6.21

# Define to build a biarch package
%define build_biarch	0
%if %isarch sparc64 x86_64 ppc64
%define build_biarch	1
%endif

# Define to build glibc-debug package
%define build_debug	1
%define _enable_debug_packages 1
%if "%{_enable_debug_packages}" == "1"
%define build_debug	0
%endif

# Define to bootstrap new glibc
%define build_bootstrap	0
%{expand: %{!?build_cross_bootstrap: %global build_cross_bootstrap 0}}

%define build_profile	1
%define build_nscd	1
%define build_doc	1
%define build_utils	1
%define build_i18ndata	1
%define build_timezone	0

# Disable a few defaults when cross-compiling a glibc
%if %{build_cross}
%define build_doc	0
%define build_pdf_doc	0
%define build_biarch	0
%define build_check	0
%define build_debug	0
%define build_nscd	0
%define build_profile	0
%define build_utils	0
%define build_i18ndata	0
%define build_timezone	0
%endif

# Allow --with[out] <feature> at rpm command line build
%{expand: %{?_without_PDF:	%%global build_pdf_doc 0}}
%{expand: %{?_without_CHECK:	%%global build_check 0}}
%{expand: %{?_without_UTILS:	%%global build_utils 0}}
%{expand: %{?_without_BOOTSTRAP:%%global build_bootstrap 0}}
%{expand: %{?_with_PDF:		%%global build_pdf_doc 1}}
%{expand: %{?_with_CHECK:	%%global build_check 1}}
%{expand: %{?_with_UTILS:	%%global build_utils 1}}
%{expand: %{?_with_BOOTSTRAP:	%%global build_bootstrap 1}}

Summary:	The GNU libc libraries
Name:		%{name}
Version:	%{glibcversion}
Release:	%{glibcrelease}
Epoch:		%{glibcepoch}
License:	LGPL
Group:		System/Libraries
Url:		http://www.gnu.org/software/libc/

# FSF source
Source0:	http://ftp.gnu.org/gnu/glibc/%{source_package}.tar.bz2
%if %{RELEASE}
Source1:	http://ftp.gnu.org/gnu/glibc/%{source_package}.tar.bz2.sig
%endif

# Red Hat tarball
Source2:	glibc-redhat.tar.bz2
Source3:	glibc-manpages.tar.bz2
Source4:	glibc-find-requires.sh
Source5:	glibc-check.sh

# If using official FSF release we must get also libidn
%if %{RELEASE}
Source6:	http://ftp.gnu.org/gnu/glibc/glibc-libidn-%{glibcversion}.tar.bz2
Source7:	http://ftp.gnu.org/gnu/glibc/glibc-libidn-%{glibcversion}.tar.bz2.sig
%endif

# wrapper to avoid rpm circular dependencies
Source14:	glibc-post-wrapper.c

# <http://penguinppc.org/dev/glibc/glibc-powerpc-cpu-addon.html>
# NOTE: this check is weak. The rationale is: Cell PPU optimized by
# default for MDV 2007.0, power5 et al. on Corporate side
%define powerpc_cpu_list noarch
%if "%{?distsuffix:%{distsuffix}}" == "mlcs4"
%define powerpc_cpu_list power5
%endif
Source15:	glibc-powerpc-cpu-addon-v0.03.tar.bz2

# Blowfish support
Source16:	crypt_blowfish-%{crypt_bf_ver}.tar.gz
Source17:	crypt_freesec.c
Source18:	crypt_freesec.h

Buildroot:	%{_tmppath}/glibc-%{PACKAGE_VERSION}-root
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Obsoletes:	zoneinfo, libc-static, libc-devel, libc-profile, libc-headers,
Obsoletes: 	linuxthreads, gencat, locale, glibc-localedata
Provides:	glibc-crypt_blowfish = %{crypt_bf_ver}
Provides:	glibc-localedata
Provides:	should-restart = system
%if %isarch %{xenarches}
Obsoletes:	%{name}-xen
Provides:	%{name}-xen
%endif
# The dynamic linker supports DT_GNU_HASH
Provides: rtld(GNU_HASH)
Autoreq:	false
%endif
BuildRequires:	patch, gettext, perl
BuildRequires:	kernel-headers
%if %{build_selinux}
BuildRequires:	libselinux-devel >= 1.17.10
%endif
# we need suitable linker for -Wl,--hash-style=both
%define binutils_version 2.16.91.0.7-%{mkrel 6}
BuildRequires:	%{cross_prefix}binutils >= %{binutils_version}
# we need the static dash
%define ash_bin		/bin/dash.static
Requires(pre):		dash-static
Requires(post):		dash-static
# we need an rpm with correct db4 lib
Conflicts:		rpm < 4.2.2
# we need an ldconfig with TLS support
%if %{build_cross}
BuildRequires:	%{cross_prefix}gcc >= 3.2.2-4mdk
%endif
%ifarch %{ix86} alpha
BuildRequires:	%{cross_prefix}gcc >= 2.96-0.50mdk
%endif
%ifarch ia64
BuildRequires:	%{cross_prefix}gcc >= 3.2.3-1mdk
%endif
%ifarch x86_64
BuildRequires:	%{cross_prefix}gcc >= 3.1.1-0.5mdk
%endif
BuildRequires:	%{cross_prefix}gcc >= 4.0.1-2mdk
%if !%{build_cross}
%ifarch alpha
Provides:	ld.so.2
%endif
%ifarch ppc
Provides:	ld.so.1
%endif
%ifarch sparc
Obsoletes:	libc
%endif
%endif

Conflicts:	rpm <= 4.0-0.65
Conflicts:	%{name}-devel < 2.2.3
# We need initscripts recent enough to not restart service dm
Conflicts:	initscripts < 6.91-18mdk
# Ease Conectiva upgrades
Conflicts:	%{name}-base <= 2.3.4

BuildRequires:	texinfo
%if %{build_pdf_doc}
BuildRequires:	tetex, tetex-latex
%endif
%if %{build_utils}
BuildRequires:	gd-devel
%endif
BuildRequires:	autoconf2.5

Patch01:	glibc-2.2.2-fhs.patch
Patch02:	glibc-2.9-ldd-non-exec.patch
Patch04:	glibc-2.2-nss-upgrade.patch
Patch06:	glibc-2.9-share-locale.patch
Patch07:	glibc-2.3.6-nsswitch.conf.patch
Patch09:	glibc-2.2.4-xterm-xvt.patch
Patch11:	glibc-2.4.90-compat-EUR-currencies.patch
Patch12:	glibc-2.3.6-ppc-build-lddlibc4.patch
Patch13:	glibc-2.3.3-nscd-enable.patch
Patch14:	glibc-2.9-nscd-no-host-cache.patch
Patch17:	glibc-2.4.90-i386-hwcapinfo.patch
Patch18:	glibc-2.7-provide_CFI_for_the_outermost_function.patch
Patch19:	glibc-2.8-nscd-init-should-start.patch
Patch22:	glibc-2.3.2-tcsetattr-kernel-bug-workaround.patch
Patch23:	glibc-2.3.4-timezone.patch
Patch24:	glibc-2.4.90-biarch-cpp-defines.patch
Patch26:	glibc-2.6-nice_fix.patch
Patch27:	glibc-2.8-ENOTTY-fr-translation.patch
Patch28:	glibc-2.4.90-gcc4-fortify.patch
Patch29:	glibc-2.3.5-biarch-utils.patch
Patch30:	glibc-2.6-multiarch.patch
Patch31:	glibc-2.4.90-i586-hptiming.patch
Patch32:	glibc-2.3.4-i586-if-no-cmov.patch
Patch33:	glibc-2.3.6-pt_BR-i18nfixes.patch
Patch34:	glibc-2.4.90-testsuite-ldbl-bits.patch
Patch36:	glibc-2.9-dns-no-gethostbyname4.patch
Patch37:	glibc-2.9-fedora_upstream_fixes.patch
Patch38:	glibc-2.4.90-testsuite-rt-notparallel.patch
Patch39:	glibc-2.9-mdv-owl-crypt_freesec.patch
Patch40:	glibc-2.9-avx-relocate_fcrypt.patch
Patch41:	glibc-2.3.6-avx-increase_BF_FRAME.patch
Patch42:	glibc-2.7-mdv-avx-owl-crypt.patch
Patch43:	glibc-2.7-mdv-wrapper_handle_sha.patch
Patch44:	glibc-2.9-dup2_avoid_access_through_PLT.patch
Patch45:	glibc-2.9-bz7067.patch
Patch46:	glibc-2.9-bz6545.patch
Patch47:	glibc-2.9-bz9694.patch
Patch48:	glibc-2.9-_nss_dns_gethostbyaddr2_r-buffer-aligment.patch
Patch49:	glibc-2.9-expm1-error.patch
Patch50:	glibc-2.9-bug-hsearch1.patch
Patch51:	glibc-2.9-bz9741.patch
Patch52:	glibc-2.9-bz9750.patch
Patch53:	glibc-2.9-SHM_EXEC.patch
Patch54:	glibc-2.9-bz7040.patch
Patch55:	glibc-2.9-bz7056.patch
Patch56:	glibc-2.9-newer-link-scripts-insert-_begin.patch

# Determine minium kernel versions
%define		enablekernel 2.6.9
%if %isarch ppc ppc64
# waitid syscall is available in 2.6.12+ there
%define		enablekernel 2.6.12
%endif
Conflicts:	kernel < %{enablekernel}

# People changed location of rpm scripts...
%define rpmscripts	/usr/lib/rpm/%{_real_vendor}

# Don't try to explicitly provide GLIBC_PRIVATE versioned libraries
%define __find_provides	%{_builddir}/%{source_dir}/find_provides.sh
%define __find_requires %{_builddir}/%{source_dir}/find_requires.sh

%if !%{build_cross}
Obsoletes:	ld.so
Provides:	ld.so
%endif

Obsoletes:	ldconfig
Provides:	ldconfig = %{glibcepoch}:%{glibcversion}-%{glibcrelease} /sbin/ldconfig

%description
The glibc package contains standard libraries which are used by
multiple programs on the system. In order to save disk space and
memory, as well as to make upgrading easier, common system code is
kept in one place and shared between programs. This particular package
contains the most important sets of shared libraries: the standard C
library and the standard math library. Without these two libraries, a
Linux system will not function.  The glibc package also contains
national language (locale) support.

This package now also provides ldconfig which was package seperately in
the past. Ldconfig is a basic system program which determines run-time
link bindings between ld.so and shared libraries. Ldconfig scans a running
system and sets up the symbolic links that are used to load shared
libraries properly. It also creates a cache (/etc/ld.so.cache) which
speeds the loading of programs which use shared libraries.

%package devel
Summary:	Header and object files for development using standard C libraries
Group:		Development/C
Conflicts:	texinfo < 3.11
Requires(post):	  info-install
Requires(preun):  info-install
Requires(post):   coreutils
Requires(postun): coreutils, awk
Obsoletes:	libc-debug, libc-headers, libc-devel, linuxthreads-devel, nptl-devel
%if !%{build_debug}
Obsoletes:	%{name}-debug < 6:2.3.2-15mdk
%endif
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}
%if !%{build_cross}
Requires:	kernel-headers
%endif
%if !%isarch ppc
Conflicts:	%{cross_prefix}gcc < 2.96-0.50mdk
%endif
# needs a gcc4 fortify capable compiler
Conflicts:	gcc4.0 < 4.0.1-2mdk
%if %{build_cross}
Autoreq:	false
Autoprov:	false
%else
Autoreq:	true
%endif
Provides:	glibc-crypt_blowfish-devel = %{crypt_bf_ver}

%description devel
The glibc-devel package contains the header and object files necessary
for developing programs which use the standard C libraries (which are
used by nearly all programs).  If you are developing programs which
will use the standard C libraries, your system needs to have these
standard header and object files available in order to create the
executables.

This package also includes the C header files for the Linux kernel.
The header files define structures and constants that are needed for
building most standard programs. The header files are also needed for
rebuilding the kernel.

Install glibc-devel if you are going to develop programs which will
use the standard C libraries.

%package static-devel
Summary:	Static libraries for GNU C library
Group:		Development/C
Requires:	%{name}-devel = %{glibcepoch}:%{glibcversion}-%{glibcrelease}

%description static-devel
The glibc-static-devel package contains the static libraries necessary
for developing programs which use the standard C libraries. Install
glibc-static-devel if you need to statically link your program or
library.

%package profile
Summary:	The GNU libc libraries, including support for gprof profiling
Group:		Development/C
Obsoletes:	libc-profile
Provides:	libc-profile = %{glibcversion}-%{glibcrelease}
Autoreq:	true

%description profile
The glibc-profile package includes the GNU libc libraries and support
for profiling using the gprof program.  Profiling is analyzing a
program's functions to see how much CPU time they use and determining
which functions are calling other functions during execution.  To use
gprof to profile a program, your program needs to use the GNU libc
libraries included in glibc-profile (instead of the standard GNU libc
libraries included in the glibc package).

If you are going to use the gprof program to profile a program, you'll
need to install the glibc-profile program.

%package -n nscd
Summary:	A Name Service Caching Daemon (nscd)
Group:		System/Servers
Conflicts:	kernel < 2.2.0
Requires(pre):	  rpm-helper
Requires(preun):  rpm-helper
Requires(post):   rpm-helper
Requires(postun): rpm-helper
Autoreq:	true

%description -n nscd
Nscd caches name service lookups and can dramatically improve
performance with NIS+, and may help with DNS as well. Note that you
can't use nscd with 2.0 kernels because of bugs in the kernel-side
thread support. Unfortunately, nscd happens to hit these bugs
particularly hard.

Install nscd if you need a name service lookup caching daemon, and
you're not using a version 2.0 kernel.

%if %{build_debug}
%package	debug
Summary:	Shared standard C libraries with debugging information
Group:		System/Libraries
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}
Autoreq:	false

%description debug
The glibc-debug package contains shared standard C libraries with
debugging information. You need this only if you want to step into C
library routines during debugging.

To use these libraries, you need to add %{_libdir}/debug to your
LD_LIBRARY_PATH variable prior to starting the debugger.
%endif

%package utils
Summary:	Development utilities from GNU C library
Group:		Development/Other
Requires:	%{name} = %{glibcepoch}:%{glibcversion}-%{glibcrelease}

%description utils
The glibc-utils package contains memusage, a memory usage profiler,
mtrace, a memory leak tracer and xtrace, a function call tracer which
can be helpful during program debugging.

If unsure if you need this, don't install this package.

%if %{build_i18ndata}
%package i18ndata
Summary:	Database sources for 'locale'
Group:		System/Libraries

%description i18ndata
This package contains the data needed to build the locale data files
to use the internationalization features of the GNU libc.
%endif

%if %{build_timezone}
%package -n timezone
Summary:	Time zone descriptions
Group:		System/Base
Conflicts:	glibc < 2.2.5-6mdk

%description -n timezone
These are configuration files that describe possible
time zones.
%endif

%package doc
Summary:	GNU C library documentation
Group:		Development/Other

%description doc
The glibc-doc package contains documentation for the GNU C library in
info format.

%if %{build_pdf_doc}
%package doc-pdf
Summary:	GNU C library documentation
Group:		Development/Other

%description doc-pdf
The glibc-doc-pdf package contains the printable documentation for the
GNU C library in PDF format.
%endif

%prep
%setup -q -n %{source_dir} -a 3 -a 2 -a 15 -a 16
%if %{RELEASE}
tar -jxf %{_sourcedir}/glibc-libidn-%{glibcversion}.tar.bz2
mv glibc-libidn-%{glibcversion} libidn
%endif

%patch01 -p1 -b .fhs
%patch02 -p1 -b .ldd-non-exec
%patch04 -p1 -b .nss-upgrade
%patch06 -p1 -b .share-locale
%patch07 -p1 -b .nsswitch.conf
%patch09 -p1 -b .xterm-xvt
%patch11 -p1 -b .compat-EUR-currencies
%patch12 -p1 -b .ppc-lddlibc4
%patch13 -p1 -b .nscd-enable
%patch14 -p1 -b .nscd-no-host-cache
%patch17 -p1 -b .i386-hwcapinfo
%patch18 -p0 -R -b .provide_CFI_for_the_outermost_function
%patch19 -p1 -b .nscd-init-should-start
%patch22 -p1 -b .tcsetattr-kernel-bug-workaround
%patch23 -p1 -b .timezone
%patch24 -p1 -b .biarch-cpp-defines
%patch26 -p1 -b .nice-fix
%patch27 -p1 -b .ENOTTY-fr-translation
%patch28 -p1 -b .gcc4-fortify
%patch29 -p1 -b .biarch-utils
%patch30 -p1 -b .multiarch-check
%patch31 -p1 -b .i586-hptiming
%patch32 -p1 -b .i586-if-no-cmov
%patch33 -p1 -b .pt_BR-i18nfixes
%patch34 -p1 -b .testsuite-ldbl-bits
%patch36 -p1 -b .dns-no-gethostbyname4
%patch37 -p1 -b .fedora_upstream_fixes
%patch38 -p1 -b .testsuite-rt-notparallel
%patch44 -p1 -b .dup2_avoid_access_through_PLT
%patch45 -p1 -b .bz7067
%patch46 -p1 -b .bz6545
%patch47 -p1 -b .bz9694
%patch48 -p1 -b ._nss_dns_gethostbyaddr2_r-buffer-aligment
%patch49 -p1 -b .expm1-error
%patch50 -p1 -b .bug-hsearch1
%patch51 -p1 -b .bz9741
%patch52 -p1 -b .bz9750
%patch53 -p1 -b .SHM_EXEC
%patch54 -p1 -b .bz7040
%patch55 -p1 -b .bz7056
%patch56 -p1 -b .newer-link-scripts-insert-_begin

# avoid backup file created with patch glibc-2.9-fedora_upstream_fixes.patch to
# end up in glibc-i18ndata package
rm -f localedata/locales/hne_IN.fedora_upstream_fixes

# copy freesec source
cp %{_sourcedir}/crypt_freesec.[ch] crypt/
echo "Applying crypt_blowfish patch:"
%patch42 -p1 -b .mdv-avx-owl-crypt
#patch -p1 -s < crypt_blowfish-%{crypt_bf_ver}/glibc-2.3.2-crypt.diff
mv crypt/crypt.h crypt/gnu-crypt.h
cp -a crypt_blowfish-%{crypt_bf_ver}/*.[chS] crypt/

## FreeSec support for extended/new-style/BSDI hashes in crypt(3)
%patch39 -p1 -b .mdv-owl-crypt_freesec
%patch40 -p1 -b .avx-relocate_fcrypt
%patch41 -p1 -b .avx-increase_BF_FRAME
# add sha256-crypt and sha512-crypt support to the Openwall wrapper
%patch43 -p0 -b .mdv-wrapper_handle_sha

%if %{build_selinux}
# XXX kludge to build nscd with selinux support as it added -nostdinc
# so /usr/include/selinux is not found
ln -s %{_includedir}/selinux selinux
%endif

find . -type f -size 0 -o -name "*.orig" -exec rm -f {} \;

# (Anssi 03/2008) FIXME: use _provides_exceptions
cat > find_provides.sh << EOF
#!/bin/sh
%{rpmscripts}/find-provides | grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_provides.sh

cat > find_requires.bootstrap.sh << EOF
/bin/sh %{SOURCE4} %{buildroot} %{_target_cpu} | grep -v "\(GLIBC_PRIVATE\|linux-gate\|linux-vdso\)"
exit 0
EOF
chmod +x find_requires.bootstrap.sh

# XXX: use better way later to avoid LD_LIBRARY_PATH issue
cat %{rpmscripts}/find-requires | sed '/.*LD_LIBRARY_PATH.*/d;' > find_requires
chmod +x find_requires
# (Anssi 03/2008) FIXME: use _requires_exceptions
cat > find_requires.noprivate.sh << EOF
%{_builddir}/%{source_dir}/find_requires %{buildroot} %{_target_cpu} | \
	grep -v GLIBC_PRIVATE
exit 0
EOF
chmod +x find_requires.noprivate.sh

# FIXME: fix system rpm find-requires to use the prefix cross version
%if %{build_bootstrap} || "%{_target_cpu}" != "%{target_cpu}"
ln -s find_requires.bootstrap.sh find_requires.sh
%else
ln -s find_requires.noprivate.sh find_requires.sh
%endif

%build
# Prepare test matrix in the next function
CheckList=$PWD/Check.list
rm -f $CheckList
touch $CheckList

#
# CompareKver <kernel version>
# function to compare the desired kernel version with running kernel
# version (package releases not taken into account in comparison). The
# function returns:
# -1 = <kernel version> is lesser than current running kernel
#  0 = <kernel version> is equal to the current running kernel
#  1 = <kernel version> is greater than current running kernel
#
function CompareKver() {
  v1=`echo $1 | sed 's/\.\?$/./'`
  v2=`uname -r | sed 's/[^.0-9].*//' | sed 's/\.\?$/./'`
  n=1
  s=0
  while true; do
    c1=`echo "$v1" | cut -d "." -f $n`
    c2=`echo "$v2" | cut -d "." -f $n`
    if [ -z "$c1" -a -z "$c2" ]; then
      break
    elif [ -z "$c1" ]; then
      s=-1
      break
    elif [ -z "$c2" ]; then
      s=1
      break
    elif [ "$c1" -gt "$c2" ]; then
      s=1
      break
    elif [ "$c2" -gt "$c1" ]; then
      s=-1
      break
    fi
    n=$((n + 1))
  done
  echo $s
}

#
# BuildGlibc <arch> [<extra_configure_options>+]
#
function BuildGlibc() {
  arch="$1"
  shift 1

  # PowerPC CPU add-on
  case $arch in
    cpu-addon,*)
      cpu=` echo "$arch" | sed -n "/.*,\([^,]*\),.*$/s//\1/p"`
      arch=`echo "$arch" | sed -n "/.*,.*,\([^,]*\)$/s//\1/p"`
      ;;
    *)
      cpu=$arch
      ;;
  esac

  # Select optimization flags and compiler to use
  BuildAltArch="no"
  BuildCompFlags=""
  BuildFlags=""
  case $arch in
    i[3456]86 | athlon)
      BuildFlags="-march=$arch -mtune=generic"
      if [[ "`uname -m`" = "x86_64" ]]; then
        BuildAltArch="yes"
        BuildCompFlags="-m32"
      fi
      ;;
    x86_64)
      BuildFlags="-mtune=generic"
      ;;
    ppc)
      if [[ "`uname -m`" = "ppc64" ]]; then
        BuildAltArch="yes"
        BuildCompFlags="-m32"
        # 64-bit processors we support do support power4+ ISA (2.01)
        if [[ "$cpu" != "$arch" ]]; then
          BuildFlags="-mcpu=$cpu"
        else
          BuildFlags="-mcpu=power4 -mtune=cell"
        fi
      fi
      ;;
    ppc64)
      if [[ "$cpu" != "$arch" ]]; then
        BuildFlags="-mcpu=$cpu"
      else
        BuildFlags="-mcpu=power4 -mtune=cell"
      fi
      ;;
    alphaev6)
      BuildFlags="-mcpu=ev6"
      ;;
    sparc)
      BuildFlags="-fcall-used-g6"
      BuildCompFlags="-m32"
      ;;
    sparcv9)
      BuildFlags="-mcpu=ultrasparc -fcall-used-g6"
      BuildCompFlags="-m32"
      ;;
    sparc64)
      BuildFlags="-mcpu=ultrasparc -mvis -fcall-used-g6"
      BuildCompFlags="-m64 -mcpu=ultrasparc"
      ;;
  esac

  # Determine C & C++ compilers
  BuildCC="%{__cc} $BuildCompFlags"
  BuildCXX="%{__cxx} $BuildCompFlags"

  # Are we supposed to cross-compile?
  if [[ "%{target_cpu}" != "%{_target_cpu}" ]]; then
    BuildCC="%{target_cpu}-linux-$BuildCC"
    BuildCXX="%{target_cpu}-linux-$BuildCXX"
    BuildCross="--build=%{_target_platform}"
    export libc_cv_forced_unwind=yes libc_cv_c_cleanup=yes
  fi

  BuildFlags="$BuildFlags -DNDEBUG=1 -O2 -finline-functions -g"
  if $BuildCC -v 2>&1 | grep -q 'gcc version 3.0'; then
    # gcc3.0 had really poor inlining heuristics causing problems in
    # resulting ld.so
    BuildFlags="$BuildFlags -finline-limit=2000"
  fi

  # Do not use direct references against %gs when accessing tls data
  # XXX make it the default in GCC? (for other non glibc specific usage)
  case $arch in
    i[3456]86 | x86_64)
      BuildFlags="$BuildFlags -mno-tls-direct-seg-refs"
      ;;
  esac

  # Disable fortify for glibc builds
  BuildFlags="$BuildFlags -U_FORTIFY_SOURCE"

  # Arch specific compilation flags
  if [[ "$arch" = "ppc64" ]]; then
    BuildFlags="$BuildFlags -fno-inline-functions -mno-minimal-toc"
  fi

  # Extra configure flags
  ExtraFlags=
  if [[ "%{build_profile}" != "0" ]]; then
    ExtraFlags="$ExtraFlags --enable-profile"
  fi

  # NPTL+TLS are now the default
  Pthreads="nptl"
  TlsFlags="--with-tls --with-__thread"

  # Add-ons
  AddOns="$Pthreads,libidn"
  if [[ "$cpu" != "$arch" ]]; then
    AddOns="$AddOns,powerpc-cpu"
    BuildFlags="$BuildFlags -mcpu=$cpu"
    ExtraFlags="$ExtraFlags --with-cpu=$cpu"
  fi

  # Build with selinux support?
%if %{build_selinux}
  SElinuxFlags="--with-selinux"
%else
  SElinuxFlags="--without-selinux"
%endif

  # Kernel headers directory
  KernelHeaders=%{_includedir}

  # Determine library name
  glibc_cv_cc_64bit_output=no
  if echo ".text" | $BuildCC -c -o test.o -xassembler -; then
    case `/usr/bin/file test.o` in
    *"ELF 64"*)
      glibc_cv_cc_64bit_output=yes
      ;;
    esac
  fi
  rm -f test.o

  # Force a separate and clean object dir
  rm -rf build-$cpu-linux
  mkdir  build-$cpu-linux
  pushd  build-$cpu-linux
  [[ "$BuildAltArch" = "yes" ]] && touch ".alt" || touch ".main"
  CC="$BuildCC" CXX="$BuildCXX" CFLAGS="$BuildFlags" ../configure \
    $arch-mandriva-linux-gnu $BuildCross \
    --prefix=%{_prefix} \
    --libexecdir=%{_prefix}/lib \
    --infodir=%{_infodir} \
    --enable-add-ons=$AddOns --without-cvs \
    $TlsFlags $ExtraFlags $SElinuxFlags \
    --enable-kernel=%{enablekernel} --with-headers=$KernelHeaders ${1+"$@"}
  %make -r PARALLELMFLAGS=-s
  popd

  # All tests are expected to pass on certain platforms, depending also
  # on the version of the kernel running
  case $arch in
  athlon | ia64 | ppc | ppc64)
    if [ "`CompareKver %{check_min_kver}`" -lt 0 ]; then
      check_flags=""
    else
      check_flags="-k"
    fi
    ;;
  *)
    check_flags="-k"
    ;;
  esac

  # Generate test matrix
  [[ -d "build-$arch-linux" ]] || {
    echo "ERROR: PrepareGlibcTest: build-$arch-linux does not exist!"
    return 1
  }
  local BuildJobs="-j`getconf _NPROCESSORS_ONLN`"
  echo "$BuildJobs -d build-$arch-linux $check_flags" >> $CheckList

  case $cpu in
  i686|athlon)	base_arch=i586;;
  power*)	base_arch=$arch;;
  *)		base_arch=none;;
  esac

  [[ -d "build-$base_arch-linux" ]] && {
    check_flags="$check_flags -l build-$base_arch-linux/elf/ld.so"
    echo "$BuildJobs -d build-$arch-linux $check_flags" >> $CheckList
  }
  return 0
}

# Build main glibc
BuildGlibc %{target_cpu}

%if %{build_biarch}
%if %isarch sparc64
BuildGlibc sparcv9
%endif
%if %isarch x86_64
BuildGlibc i686
%endif
%if %isarch ppc64
BuildGlibc ppc
%endif
%endif

%if %isarch ppc ppc64
for cpu in %{powerpc_cpu_list}; do
  [[ "$cpu" = "noarch" ]] && continue
  BuildGlibc cpu-addon,$cpu,%{_arch} --disable-profile
done
%endif

# Build i686 libraries if not already building for i686/athlon
case %{target_cpu} in
  i686 | athlon)
    ;;
  i[3-6]86)
    BuildGlibc i686 --disable-profile
    ;;
esac

make -C crypt_blowfish-%{crypt_bf_ver} man

%if %{build_check}
export TMPDIR=/tmp
export TIMEOUTFACTOR=16
Check="$PWD/glibc-check.sh"
cat %{SOURCE5} > $Check
chmod +x $Check
while read arglist; do
  $Check $arglist || exit 1
done < $CheckList
%endif

%install
rm -rf $RPM_BUILD_ROOT

# force use of _NPROCESSORS_ONLN jobs since RPM_BUILD_NCPUS could be
# greater for icecream
BuildJobs="-j`getconf _NPROCESSORS_ONLN`"

make install_root=$RPM_BUILD_ROOT install -C build-%{target_cpu}-linux
%if %{build_i18ndata}
(cd build-%{target_cpu}-linux;
  make $BuildJobs -C ../localedata objdir=`pwd` \
	install_root=$RPM_BUILD_ROOT \
	install-locales
)
%endif
sh manpages/Script.sh

# Empty filelist for non i686/athlon targets
> extralibs.filelist

# Install biarch libraries
%if %{build_biarch}
%if %isarch sparc64
ALT_ARCH=sparcv9-linux
%endif
%if %isarch x86_64
ALT_ARCH=i686-linux
%endif
%if %isarch ppc64
ALT_ARCH=ppc-linux
%endif
mkdir -p $RPM_BUILD_ROOT/$ALT_ARCH
make install_root=$RPM_BUILD_ROOT/$ALT_ARCH install -C build-$ALT_ARCH

# Dispatch */lib only
mv $RPM_BUILD_ROOT/$ALT_ARCH/lib $RPM_BUILD_ROOT/
rm -f  $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/pt_chown
mv     $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/getconf/* $RPM_BUILD_ROOT%{_prefix}/lib/getconf/
rmdir  $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/getconf
mv     $RPM_BUILD_ROOT/$ALT_ARCH%{_prefix}/lib/* $RPM_BUILD_ROOT%{_prefix}/lib/
# We want 32-bit binaries on sparc64
%if %isarch sparc64
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/sbin/* $RPM_BUILD_ROOT/sbin
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/%{_bindir}/* $RPM_BUILD_ROOT%{_bindir}
mv -f    $RPM_BUILD_ROOT/$ALT_ARCH/%{_sbindir}/* $RPM_BUILD_ROOT%{_sbindir}
%endif
rm -rf $RPM_BUILD_ROOT/$ALT_ARCH
# XXX Dispatch 32-bit stubs
(sed '/^@/d' include/stubs-prologue.h; LC_ALL=C sort $(find build-$ALT_ARCH -name stubs)) \
> $RPM_BUILD_ROOT%{_includedir}/gnu/stubs-32.h
%endif

# Install extra glibc libraries
function InstallGlibc() {
  local BuildDir="$1"
  local SubDir="$2"
  local LibDir="$3"

  case $BuildDir in
  *)      Pthreads=nptl         ;;
  esac

  [[ -z "$LibDir" ]] && LibDir="%{_slibdir}"

  pushd $BuildDir
  mkdir -p $RPM_BUILD_ROOT$LibDir/$SubDir/
  install -m755 libc.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libc-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libc-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libc.so.*`
  install -m755 math/libm.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libm-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libm-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libm.so.*`
  install -m755 $Pthreads/libpthread.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libpthread-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libpthread-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libpthread.so.*`
  install -m755 ${Pthreads}_db/libthread_db.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libthread_db-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/libthread_db-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/libthread_db.so.*`
  install -m755 rt/librt.so $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/librt-*.so`
  ln -sf `basename $RPM_BUILD_ROOT$LibDir/librt-*.so` $RPM_BUILD_ROOT$LibDir/$SubDir/`basename $RPM_BUILD_ROOT$LibDir/librt.so.*`
  echo "%dir $LibDir/$SubDir" >> ../extralibs.filelist
  find $RPM_BUILD_ROOT$LibDir/$SubDir -maxdepth 1  -type f -o -type l | sed -e "s|$RPM_BUILD_ROOT||" >> ../extralibs.filelist
  popd
}

# Install arch-specific optimized libraries
%if %isarch %{ix86}
case %{target_cpu} in
i[3-5]86)
  InstallGlibc build-i686-linux i686
  ;;
esac
%endif
%if %isarch ppc ppc64
for cpu in %{powerpc_cpu_list}; do
  [[ "$cpu" = "noarch" ]] && continue
  InstallGlibc build-$cpu-linux $cpu
done
# Use hardlinks, not symlinks
# see upper NOTE if you really want dedicated power5+ hwcap...
[[ -d "$RPM_BUILD_ROOT/%{_lib}/power5" ]] && {
  mkdir -p $RPM_BUILD_ROOT/%{_lib}/power5+
  ln -v	$RPM_BUILD_ROOT/%{_lib}/power5/*.so \
	$RPM_BUILD_ROOT/%{_lib}/power5+/
  $RPM_BUILD_ROOT/sbin/ldconfig -n $RPM_BUILD_ROOT/%{_lib}/power5+/
  echo "%dir /%{_lib}/power5+" >> extralibs.filelist
  find $RPM_BUILD_ROOT$LibDir/%{_lib}/power5+/ -maxdepth 1  -type f -o -type l | sed -e "s|$RPM_BUILD_ROOT||" >> extralibs.filelist
}
%endif

# NPTL <bits/stdio-lock.h> is not usable outside of glibc, so include
# the generic one (RH#162634)
install -m644 bits/stdio-lock.h $RPM_BUILD_ROOT%{_includedir}/bits/stdio-lock.h

# Compatibility hack: this locale has vanished from glibc, but some other
# programs are still using it. Normally we would handle it in the %pre
# section but with glibc that is simply not an option
mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/ru_RU/LC_MESSAGES

# Remove the files we don't want to distribute
rm -f $RPM_BUILD_ROOT%{_libdir}/libNoVersion*
rm -f $RPM_BUILD_ROOT%{_slibdir}/libNoVersion*

ln -sf libbsd-compat.a $RPM_BUILD_ROOT%{_libdir}/libbsd.a
%if %{build_biarch}
ln -sf libbsd-compat.a $RPM_BUILD_ROOT%{_prefix}/lib/libbsd.a
%endif

%if "%{name}" == "glibc"
install -m 644 mandriva/nsswitch.conf $RPM_BUILD_ROOT%{_sysconfdir}/nsswitch.conf
%endif

# Take care of setuids
# -- new security review sez that this shouldn't be needed anymore
#chmod 755 $RPM_BUILD_ROOT%{_libdir}/pt_chown

# This is for ncsd - in glibc 2.2
%if %{build_nscd}
install -m 644 nscd/nscd.conf $RPM_BUILD_ROOT%{_sysconfdir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
install -m 755 nscd/nscd.init $RPM_BUILD_ROOT%{_initrddir}/nscd
%endif

# These man pages require special attention
mkdir -p %{buildroot}%{_mandir}/man3
install -p -m 0644 crypt_blowfish-%{crypt_bf_ver}/*.3 %{buildroot}%{_mandir}/man3/

# Useless and takes place
rm -rf %buildroot/%{_datadir}/zoneinfo/{posix,right}

# Include ld.so.conf
%if "%{name}" == "glibc"
echo "include /etc/ld.so.conf.d/*.conf" > $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf
chmod 644 $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf
mkdir -p  $RPM_BUILD_ROOT%{_sysconfdir}/ld.so.conf.d
%endif

# ldconfig cache
mkdir -p $RPM_BUILD_ROOT%{_var}/cache/ldconfig
touch $RPM_BUILD_ROOT%{_var}/cache/ldconfig/aux-cache

# automatic ldconfig cache update on rpm installs/removals
# (see http://wiki.mandriva.com/en/Rpm_filetriggers)
install -d %buildroot%{_var}/lib/rpm/filetriggers
cat > %buildroot%{_var}/lib/rpm/filetriggers/ldconfig.filter << EOF
^.((/lib|/usr/lib)(64)?/[^/]*\.so\.|/etc/ld.so.conf.d/[^/]*\.conf)
EOF
cat > %buildroot%{_var}/lib/rpm/filetriggers/ldconfig.script << EOF
#!/bin/sh
ldconfig -X
EOF
chmod 755 %buildroot%{_var}/lib/rpm/filetriggers/ldconfig.script

# Include %{_libdir}/gconv/gconv-modules.cache
> $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache
chmod 644 $RPM_BUILD_ROOT%{_libdir}/gconv/gconv-modules.cache

# Add libraries to debug sub-package
%if %{build_debug}
mkdir $RPM_BUILD_ROOT%{_libdir}/debug
#cp -a $RPM_BUILD_ROOT%{_libdir}/*.a $RPM_BUILD_ROOT%{_libdir}/debug/
#rm -f $RPM_BUILD_ROOT%{_libdir}/debug/*_p.a
cp -a $RPM_BUILD_ROOT%{_slibdir}/lib*.so* $RPM_BUILD_ROOT%{_libdir}/debug/

pushd $RPM_BUILD_ROOT%{_libdir}/debug
for lib in *.so*; do
  [[ -f "$lib" ]] && DEBUG_LIBS="$DEBUG_LIBS %{_libdir}/debug/$lib"
done
popd
%endif

# Are we cross-compiling?
Strip="strip"
if [[ "%{_target_cpu}" != "%{target_cpu}" ]]; then
  Strip="%{target_cpu}-linux-$Strip"
fi

# Strip libpthread but keep some symbols
find $RPM_BUILD_ROOT%{_slibdir} -type f -name "libpthread-*.so" | \
     xargs $Strip -g -R .comment

%if %{build_biarch}
find $RPM_BUILD_ROOT/lib -type f -name "libpthread-*.so" | \
     xargs $Strip -g -R .comment
%endif

# Strip debugging info from all static libraries
pushd $RPM_BUILD_ROOT%{_libdir}
for i in *.a; do
  if [ -f "$i" ]; then
    case "$i" in
    *_p.a) ;;
    *) $Strip -g -R .comment $i ;;
    esac
  fi
done
popd

# post install wrapper
%__cc -Os -DSLIBDIR="\"%{_slibdir}\"" -DASH_BIN="\"%{ash_bin}\"" %{SOURCE14} -static \
	-L $RPM_BUILD_ROOT%{_libdir}/ \
	-o $RPM_BUILD_ROOT%{_sbindir}/glibc-post-wrapper
chmod 700 $RPM_BUILD_ROOT%{_sbindir}/glibc-post-wrapper

# rquota.x and rquota.h are now provided by quota
rm -f $RPM_BUILD_ROOT%{_includedir}/rpcsvc/rquota.[hx]

# Hardlink identical locale files together
%if %{build_i18ndata}
gcc -O2 -o build-%{_target_cpu}-linux/hardlink redhat/hardlink.c
build-%{_target_cpu}-linux/hardlink -vc $RPM_BUILD_ROOT%{_datadir}/locale
%endif

rm -rf $RPM_BUILD_ROOT%{_includedir}/netatalk/

# Build file list for devel package
find $RPM_BUILD_ROOT%{_includedir} -type f -or -type l > devel.filelist
find $RPM_BUILD_ROOT%{_includedir} -type d  | sed "s/^/%dir /" | \
  grep -v "%{_libdir}/libnss1.*.so$" | \
  grep -v "%{_includedir}$" | >> devel.filelist
find $RPM_BUILD_ROOT%{_libdir} -maxdepth 1 -name "*.so" -o -name "*.o" | egrep -v "(libmemusage.so|libpcprofile.so)" >> devel.filelist
# biarch libs
%if %{build_biarch}
find $RPM_BUILD_ROOT%{_prefix}/lib -maxdepth 1 -name "*.so" -o -name "*.o" | egrep -v "(libmemusage.so|libpcprofile.so)" >> devel.filelist
%endif
perl -pi -e "s|$RPM_BUILD_ROOT||" devel.filelist

# /etc/localtime - we're proud of our timezone #Well we(mdk) may put Paris
%if %{build_timezone}
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/localtime
cp -f $RPM_BUILD_ROOT%{_datadir}/zoneinfo/US/Eastern $RPM_BUILD_ROOT%{_sysconfdir}/localtime
#ln -sf ..%{_datadir}/zoneinfo/US/Eastern $RPM_BUILD_ROOT%{_sysconfdir}/localtime
%endif

# [gg] build PDF documentation
%if %{build_pdf_doc}
(cd manual; texi2dvi -p -t @afourpaper -t @finalout libc.texinfo)
%endif

# the last bit: more documentation
rm -rf documentation
mkdir documentation
cp timezone/README documentation/README.timezone
cp ChangeLog* documentation
gzip -9 documentation/ChangeLog*
mkdir documentation/crypt_blowfish-%{crypt_bf_ver}
cp crypt_blowfish-%{crypt_bf_ver}/{README,LINKS,PERFORMANCE} \
    documentation/crypt_blowfish-%{crypt_bf_ver}

# Generate final rpm filelist, with localized libc.mo files
rm -f rpm.filelist
%if "%{name}" == "glibc"
%find_lang libc
perl -ne '/^\s*$/ or print' libc.lang > rpm.filelist
%endif
cat extralibs.filelist >> rpm.filelist

# Remove unpackaged files
rm -f  $RPM_BUILD_ROOT%{_infodir}/dir.old*
rm -f  $RPM_BUILD_ROOT%{_prefix}/lib/pt_chown
rm -rf $RPM_BUILD_ROOT%{_includedir}/asm-*/mach-*/
rm -f  $RPM_BUILD_ROOT%{_datadir}/locale/locale-archive*

%if !%{build_utils}
%if %{build_biarch}
rm -f  $RPM_BUILD_ROOT%{_slibdir32}/libmemusage.so
rm -f  $RPM_BUILD_ROOT%{_slibdir32}/libpcprofile.so
%endif
rm -f  $RPM_BUILD_ROOT%{_slibdir}/libmemusage.so
rm -f  $RPM_BUILD_ROOT%{_slibdir}/libpcprofile.so
rm -f  $RPM_BUILD_ROOT%{_bindir}/memusage
rm -f  $RPM_BUILD_ROOT%{_bindir}/memusagestat
rm -f  $RPM_BUILD_ROOT%{_bindir}/mtrace
rm -f  $RPM_BUILD_ROOT%{_bindir}/pcprofiledump
rm -f  $RPM_BUILD_ROOT%{_bindir}/xtrace
%endif

%if !%{build_timezone}
rm -f  $RPM_BUILD_ROOT%{_sysconfdir}/localtime
rm -f  $RPM_BUILD_ROOT%{_sbindir}/zdump
rm -f  $RPM_BUILD_ROOT%{_sbindir}/zic
rm -f  $RPM_BUILD_ROOT%{_mandir}/man1/zdump.1*
rm -rf $RPM_BUILD_ROOT%{_datadir}/zoneinfo
%endif

%if !%{build_i18ndata}
rm -rf $RPM_BUILD_ROOT%{_datadir}/i18n
%endif

%if "%{name}" != "glibc"
rm -rf $RPM_BUILD_ROOT/boot
rm -rf $RPM_BUILD_ROOT/sbin
rm -rf $RPM_BUILD_ROOT/usr/share
rm -rf $RPM_BUILD_ROOT%{_bindir}
rm -rf $RPM_BUILD_ROOT%{_sbindir}
rm -rf $RPM_BUILD_ROOT%{_datadir}
rm -rf $RPM_BUILD_ROOT%{_mandir}
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -rf $RPM_BUILD_ROOT%{_prefix}/etc
rm -rf $RPM_BUILD_ROOT%{_libdir}/gconv
%endif

# In case we are cross-compiling, don't bother to remake symlinks and
# fool spec-helper when stripping files
%if "%{name}" != "glibc"
export DONT_SYMLINK_LIBS=1
export PATH=%{_bindir}:$PATH
%endif

EXCLUDE_FROM_STRIP="ld-%{glibcversion}.so libpthread $DEBUG_LIBS"
export EXCLUDE_FROM_STRIP

%if "%{name}" == "glibc"
%define upgradestamp %{_slibdir}/glibc.upgraded
%define broken_link %{_slibdir}/libnss_nis.so.1 %{_slibdir}/libnss_files.so.1 %{_slibdir}/libnss_dns.so.1 %{_slibdir}/libnss_compat.so.1

%pre -p %{ash_bin}
# test(1) and echo(1) are built-ins
if [ -d %{_slibdir} ] && [ ! -f %{_slibdir}/libnss_files-%{glibcversion}.so ]; then
  echo > %{upgradestamp}
fi

%post -p %{_sbindir}/glibc-post-wrapper
export LC_ALL=C

if [ "$1" -gt 1 ]; then
  # migrate /etc/ld.so.conf to include the new /etc/ld.so.conf.d/
  # without external commands but for removing the temporary file
  ldso_conf=/etc/ld.so.conf
  while read i; do
    [ "$i" = "include /etc/ld.so.conf.d/*.conf" ] && keep=1
    # Remove previously used include line without absolute path
    [ "$i" = "include ld.so.conf.d/*.conf" ] || echo $i
  done < $ldso_conf > $ldso_conf-
  if [ -z "$keep" ]; then
    echo "include /etc/ld.so.conf.d/*.conf" > $ldso_conf
    while read i; do
      echo $i
    done < $ldso_conf- >> $ldso_conf
  fi
  [ -x /bin/rm ] && /bin/rm -f $ldso_conf-
fi
/sbin/ldconfig

if [ "$1" -gt 1 ]; then
  # On upgrade the services doesn't work because libnss couldn't be
  # loaded anymore.
  if [ -f %{upgradestamp} ]; then
    if /usr/bin/readlink /proc/1/exe >/dev/null && \
       /usr/bin/readlink /proc/1/root >/dev/null; then
       if [ -x /sbin/telinit -a -p /dev/initctl ]; then
         /sbin/telinit u
       fi
       if [ -x /etc/init.d/sshd -a \
            -x /usr/sbin/sshd -a \
            -x /bin/bash ]; then
         /etc/init.d/sshd condrestart
       fi
    fi
  fi
  if [ -f /bin/rm ]; then
    for i in %broken_link; do
      if [ -e $i ] && [ ! -L $i ]; then
        /bin/rm -f $i
      fi
    done
  fi
fi
[ -x /bin/rm ] && /bin/rm -f %{upgradestamp}

# always generate the gconv-modules.cache
%{_sbindir}/iconvconfig -o %{_libdir}/gconv/gconv-modules.cache --nostdlib %{_libdir}/gconv

%if %mdkversion < 200900
%postun -p /sbin/ldconfig
%endif
%endif

%pre devel
if [ -L %{_includedir}/scsi ]; then
  rm -f %{_includedir}/scsi
fi
if [ -L %{_includedir}/sound ]; then
  rm -f %{_includedir}/sound
fi
if [ -L %{_includedir}/linux ]; then
  rm -f %{_includedir}/linux
fi
if [ -L %{_includedir}/asm ]; then
  rm -f %{_includedir}/asm
fi
if [ -L %{_includedir}/asm-generic ]; then
  rm -f %{_includedir}/asm-generic
fi
%if %isarch x86_64
if [ -L %{_includedir}/asm-x86_64 ]; then
  rm -f %{_includedir}/asm-x86_64
fi
if [ -L %{_includedir}/asm-i386 ]; then
  rm -f %{_includedir}/asm-i386
fi
%endif
%if %isarch ppc64
if [ -L %{_includedir}/asm-ppc64 ]; then
  rm -f %{_includedir}/asm-ppc64
fi
if [ -L %{_includedir}/asm-ppc ]; then
  rm -f %{_includedir}/asm-ppc
fi
%endif
%if %isarch sparc64
if [ -L %{_includedir}/asm-sparc64 ]; then
  rm -f %{_includedir}/asm-sparc64
fi
if [ -L %{_includedir}/asm-sparc ]; then
  rm -f %{_includedir}/asm-sparc
fi
%endif
exit 0

%if %{build_doc}
%post doc
%_install_info libc.info

%preun doc
%_remove_install_info libc.info
%endif

%if %{build_utils}
%if %mdkversion < 200900
%post utils -p /sbin/ldconfig
%endif
%if %mdkversion < 200900
%postun utils -p /sbin/ldconfig
%endif
%endif

%if %{build_nscd}
%pre -n nscd
%_pre_useradd nscd / /bin/false

%post -n nscd
%_post_service nscd

%preun -n nscd
%_preun_service nscd

%postun -n nscd
%_postun_userdel nscd

if [ "$1" -ge "1" ]; then
  /sbin/service nscd condrestart > /dev/null 2>&1 || :
fi
%endif

%clean
#rm -rf "$RPM_BUILD_ROOT"
#rm -f *.filelist*

#
# glibc
#
%files -f rpm.filelist
%defattr(-,root,root)
%if "%{name}" == "glibc"
%if %{build_timezone}
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/localtime
%endif
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/nsswitch.conf
%verify(not md5 size mtime) %config(noreplace) %{_sysconfdir}/ld.so.conf
%dir %{_sysconfdir}/ld.so.conf.d
%config(noreplace) %{_sysconfdir}/rpc
%doc posix/gai.conf
%{_mandir}/man1/*
%{_mandir}/man8/rpcinfo.8*
%{_mandir}/man8/ld.so*
%{_datadir}/locale/locale.alias
/sbin/sln
%dir %{_prefix}/lib/getconf
%{_prefix}/lib/getconf/*
%endif
%{_slibdir}/ld-%{glibcversion}.so
%if %isarch i386 alpha sparc sparc64
%{_slibdir}/ld-linux.so.2
%endif
%if %isarch ppc
%{_slibdir}/ld.so.1
%endif
%if %isarch ppc64
%{_slibdir}/ld64.so.1
%endif
%if %isarch ia64
%{_slibdir}/ld-linux-ia64.so.2
%endif
%if %isarch x86_64
%{_slibdir}/ld-linux-x86-64.so.2
%endif
%if %isarch m68k
%{_slibdir}/ld.so.1
%endif
%{_slibdir}/lib*-[.0-9]*.so
%{_slibdir}/lib*.so.[0-9]*
%{_slibdir}/libSegFault.so
%if "%{name}" == "glibc"
%dir %{_libdir}/gconv
%{_libdir}/gconv/*.so
%{_libdir}/gconv/gconv-modules
%ghost %{_libdir}/gconv/gconv-modules.cache
# Don't package pt_chown. It is only needed if devpts is not used. But
# since we are running kernel 2.4+, that's fine without.
# (and it never actually worked, aka was not setuid, nor executable)
#%{_libdir}/pt_chown
%{_bindir}/catchsegv
%{_bindir}/gencat
%{_bindir}/getconf
%{_bindir}/getent
#%{_bindir}/glibcbug
%{_bindir}/iconv
%{_bindir}/ldd
%if %isarch i386 ppc sparc sparc64
%{_bindir}/lddlibc4
%endif
%{_bindir}/locale
%{_bindir}/localedef
%{_bindir}/rpcgen
%{_bindir}/sprof
%{_bindir}/tzselect
%{_sbindir}/rpcinfo
%{_sbindir}/iconvconfig
%{_sbindir}/glibc-post-wrapper
%endif

%if %{build_biarch}
%{_slibdir32}/ld-%{glibcversion}.so
%if %isarch ppc64
%{_slibdir32}/ld.so.1
%else
%{_slibdir32}/ld-linux*.so.2
%endif
%{_slibdir32}/lib*-[.0-9]*.so
%{_slibdir32}/lib*.so.[0-9]*
%{_slibdir32}/libSegFault.so
%dir %{_prefix}/lib/gconv
%{_prefix}/lib/gconv/*
%endif
#
# ldconfig
#
%if "%{name}" == "glibc"
%defattr(-,root,root)
/sbin/ldconfig
%{_mandir}/man8/ldconfig*
%ghost %{_sysconfdir}/ld.so.cache
%dir %{_var}/cache/ldconfig
%ghost %{_var}/cache/ldconfig/aux-cache
%{_var}/lib/rpm/filetriggers/ldconfig.*
%endif

#
# glibc-devel
#
%files devel -f devel.filelist
%defattr(-,root,root)
%doc README NEWS INSTALL FAQ BUGS NOTES PROJECTS CONFORMANCE
%doc COPYING COPYING.LIB
%doc documentation/* README.libm
%doc hesiod/README.hesiod
%doc crypt/README.ufc-crypt
%{_mandir}/man3/*
%{_libdir}/libbsd-compat.a
%{_libdir}/libbsd.a
%{_libdir}/libc_nonshared.a
%{_libdir}/libg.a
%{_libdir}/libieee.a
%{_libdir}/libmcheck.a
%{_libdir}/libpthread_nonshared.a
%if "%{name}" == "glibc"
%{_libdir}/librpcsvc.a
%endif
%if %isarch ppc ppc64 sparc
%{_libdir}/libnldbl_nonshared.a
%endif

%if %{build_biarch}
%{_prefix}/lib/libbsd-compat.a
%{_prefix}/lib/libbsd.a
%{_prefix}/lib/libc_nonshared.a
%{_prefix}/lib/libg.a
%{_prefix}/lib/libieee.a
%{_prefix}/lib/libmcheck.a
%{_prefix}/lib/libpthread_nonshared.a
%{_prefix}/lib/librpcsvc.a
%if %isarch ppc64 sparc64
%{_prefix}/lib/libnldbl_nonshared.a
%endif
%endif

#
# glibc-static-devel
#
%files static-devel
%defattr(-,root,root)
%doc COPYING COPYING.LIB
%{_libdir}/libBrokenLocale.a
%{_libdir}/libanl.a
%{_libdir}/libc.a
%{_libdir}/libcrypt.a
%{_libdir}/libdl.a
%{_libdir}/libm.a
%{_libdir}/libnsl.a
%{_libdir}/libpthread.a
%{_libdir}/libresolv.a
%{_libdir}/librt.a
%{_libdir}/libutil.a

%if %{build_biarch}
%{_prefix}/lib/libBrokenLocale.a
%{_prefix}/lib/libanl.a
%{_prefix}/lib/libc.a
%{_prefix}/lib/libcrypt.a
%{_prefix}/lib/libdl.a
%{_prefix}/lib/libm.a
%{_prefix}/lib/libnsl.a
%{_prefix}/lib/libpthread.a
%{_prefix}/lib/libresolv.a
%{_prefix}/lib/librt.a
%{_prefix}/lib/libutil.a
%endif

#
# glibc-doc
#
%if %{build_doc}
%files doc
%defattr(-,root,root)
%{_infodir}/libc.info*
%endif

#
# glibc-doc-pdf
#
%if %{build_pdf_doc}
%files doc-pdf
%defattr(-,root,root)
%doc manual/libc.pdf
%endif

#
# glibc-debug
#
%if %{build_debug}
%files debug
%defattr(-,root,root)
%dir %{_libdir}/debug
%{_libdir}/debug/*.so
%{_libdir}/debug/*.so.*
%endif

#
# glibc-profile
#
%if %{build_profile}
%files profile
%defattr(-,root,root)
%{_libdir}/lib*_p.a
%if %{build_biarch}
%{_prefix}/lib/lib*_p.a
%endif
%endif

#
# glibc-utils
#
%if %{build_utils}
%files utils
%defattr(-,root,root)
%if %{build_biarch}
%{_slibdir32}/libmemusage.so
%{_slibdir32}/libpcprofile.so
%endif
%{_slibdir}/libmemusage.so
%{_slibdir}/libpcprofile.so
%{_bindir}/memusage
%{_bindir}/memusagestat
%{_bindir}/mtrace
%{_bindir}/pcprofiledump
%{_bindir}/xtrace
%endif

#
# nscd
#
%if %{build_nscd}
%files -n nscd
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/nscd.conf
%config(noreplace) %{_initrddir}/nscd
%{_sbindir}/nscd
%endif

#
# timezone
#
%if %{build_timezone}
%files -n timezone
%defattr(-,root,root)
%{_sbindir}/zdump
%{_sbindir}/zic
%{_mandir}/man1/zdump.1*
%dir %{_datadir}/zoneinfo
%{_datadir}/zoneinfo/*
%endif

#
# glibc-i18ndata
#
%if %{build_i18ndata}
%files i18ndata
%defattr(-,root,root)
%dir %{_datadir}/i18n
%dir %{_datadir}/i18n/charmaps
%{_datadir}/i18n/charmaps/*
%dir %{_datadir}/i18n/locales
%{_datadir}/i18n/locales/*
%endif


