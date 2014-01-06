%define _unpackaged_files_terminate_build 0
%define name blackbird-httpd
%define version 0.1.1
%define unmangled_version 0.1.1
%define release 1

%define blackbird_conf_dir /etc/blackbird/conf.d

Summary: Get monitorring stats of httpd for blackbird
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: makocchi <makocchi@gmail.com>
Packager: makocchi <makocchi@gmail.com>
Requires:  blackbird
Url: https://github.com/Vagrants/blackbird-httpd
BuildRequires:  python-devel

%description
Project Info
============

* Project Page: https://github.com/Vagrants/blackbird-httpd


%prep
%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install --skip-build --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT/%{blackbird_conf_dir}
cp -p httpd.cfg $RPM_BUILD_ROOT/%{blackbird_conf_dir}/httpd.cfg

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Mon Jan 6 2014 makochi <makocchi@gmail.com> - 0.1.1
- version up to 0.1.1

* Wed Nov 25 2013 makochi <makocchi@gmail.com> - 0.1.0
- first package
