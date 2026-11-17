Name:		scala-213-part1
Version:	1
Release:	1
Summary:	First Scala 2.13.16 checkpoint, through v2.11.6
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/scala/scala
Source0:	scala-2.13.16.tar.gz
Source1:	scala-official-objects.tar
Source2:	java-diff-utils-git.tar
Source3:	scala-213-drivers.tar

BuildArch:	noarch
BuildRequires:	scala-bootstrap = 2.10.7
BuildRequires:	java-1.8.0-openjdk-devel
BuildRequires:	git-core
BuildRequires:	make
BuildRequires:	python
BuildRequires:	tar
BuildRequires:	unzip

%description
Checkpoint of the Scala 2.13.16 source climb from v2.11.0-M1 through
v2.11.6. It starts from the scala-bootstrap 2.10.7 jars. The slimmed
v2.11.6 pack is the starr compiler for v2.12.0-M1. This package does
not provide the Scala 2.13.16 compiler.

%prep
%autosetup -n scala-2.13.16
tar -xf %{SOURCE3}
set -euo pipefail
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -s LICENSE
test -s compile.sh
test -s check.sh
test -s prune-stage.sh
test -s Hello.scala
test -s build-211m1.sh
test -s build-direct-chain.sh
grep -q SCALA_213_FROM compile.sh
grep -q SCALA_213_SEED compile.sh
grep -q SCALA_213_FROM_PENDING build-direct-chain.sh
test -s scripts/scalac
test -d scala-official.git
test -s vendor/apache-ant-1.9.16/bootstrap.sh
/bin/rm -f scala-official.git/objects/info/alternates
/bin/mkdir -p scala-official.git/objects/pack
tar -xf %{SOURCE1} -C scala-official.git/objects/pack
/bin/rm -rf scala-official.git/worktrees
sed -i 's#^	url = /home/bero/.*#	url = .#' scala-official.git/config deps/scala-asm.git/config
test ! -e scala-official.git/objects/info/alternates
pack=$(find scala-official.git/objects/pack -name '*.pack' -type f)
test -s "$pack"
git --git-dir="$PWD/scala-official.git" rev-parse --verify "v2.11.0-M1^{commit}"
git --git-dir="$PWD/scala-official.git" rev-parse --verify "v2.11.6^{commit}"
grep -F -q 'url = .' scala-official.git/config
grep -F -q 'url = .' deps/scala-asm.git/config
if grep -F -q /home/bero scala-official.git/config deps/scala-asm.git/config; then
	echo "host path remains in git config"
	exit 1
fi
/bin/rm -rf vendor-src/java-diff-utils
/bin/mkdir -p vendor-src/java-diff-utils
tar -xf %{SOURCE2} -C vendor-src/java-diff-utils
test -d vendor-src/java-diff-utils/.git
git -C vendor-src/java-diff-utils rev-parse --verify "java-diff-utils-parent-4.12^{commit}"
git -C vendor-src/java-diff-utils rev-parse --verify "java-diff-utils-parent-4.15^{commit}"

%build
set -eo pipefail
export JAVA_HOME=$(ls -d %{_jvmdir}/java-1.8.0-openjdk-* | head -n 1)
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
export SCALA_213_FROM=v2.11.0-M1
export SCALA_213_UNTIL=v2.11.6
bash ./compile.sh

%install
set -eo pipefail
dest=%{buildroot}%{_datadir}/scala-213-part1/seed
/bin/mkdir -p "$dest/official-2116" "$dest/verify/v2.11.6"
/bin/cp -a official-2116/. "$dest/official-2116/"
/bin/rm -rf "$dest/official-2116/.git"
if [ -s verify/v2.11.6/run.log ]; then
	/bin/cp -a verify/v2.11.6/run.log "$dest/verify/v2.11.6/run.log"
fi
printf '%s\n' v2.11.6 > "$dest/until-stage"
printf '%s\n' v2.12.0-M1 > "$dest/next-stage"
test -s "$dest/official-2116/build/pack/lib/scala-library.jar"
test -s "$dest/official-2116/build/pack/lib/scala-reflect.jar"
test -s "$dest/official-2116/build/pack/lib/scala-compiler.jar"
test -x "$dest/official-2116/build/pack/bin/scalac"
test ! -e "$dest/official-2116/src"
grep -qx v2.11.6 "$dest/until-stage"
grep -qx v2.12.0-M1 "$dest/next-stage"

%check
set -eo pipefail
export JAVA_HOME=$(ls -d %{_jvmdir}/java-1.8.0-openjdk-* | head -n 1)
export PATH="$JAVA_HOME/bin:/usr/bin:/bin"
out=$(bash ./check.sh %{buildroot}%{_datadir}/scala-213-part1/seed/official-2116/build/pack)
printf '%s\n' "$out"
test "$out" = "scala_stage_ok 42"

%files
%{_datadir}/scala-213-part1
%license LICENSE
