from __future__ import unicode_literals

import six

from . import errors
from .base import FS
from .copy import copy_file
from .info import Info
from .move import move_file
from .path import abspath, normpath


@six.python_2_unicode_compatible
class WrapFS(FS):
    """"
    A proxy for a filesystem object.

    This class exposes an filesystem interface, where the data is
    stored on another filesystem(s), and is the basis for
    :class:`fs.subfs.SubFS` and other *virtual* filesystems.

    """

    wrap_name = None

    def __init__(self, wrap_fs):
        self._wrap_fs = wrap_fs
        super(WrapFS, self).__init__()

    def __repr__(self):
        return "{}({!r})".format(
            self.__class__.__name__,
            self._wrap_fs
        )

    def __str__(self):
        wraps = []
        _fs = self
        while hasattr(_fs, '_wrap_fs'):
            wrap_name = getattr(_fs, 'wrap_name', None)
            if wrap_name is not None:
                wraps.append(wrap_name)
            _fs = _fs._wrap_fs
        if wraps:
            _str = "{}({})".format(_fs, ', '.join(wraps[::-1]))
        else:
            _str = "{}".format(_fs)
        return _str

    def delegate_path(self, path):
        """
        Encode a path for proxied filesystem.

        :param path: A path on the fileystem.
        :type path: str
        :returns: a tuple of <filesystem>, <new path>
        :rtype: tuple

        """
        return self._wrap_fs, path

    def delegate_fs(self):
        """
        Get the filesystem.

        This method should return a filesystem for methods not
        associated with a path, e.g. :meth:`fs.base.FS.getmeta`.

        """
        return self._wrap_fs

    def on_write(self):
        pass

    def getinfo(self, path, *namespaces):
        self._check()
        _fs, _path = self.delegate_path(path)
        raw_info = _fs.getinfo(_path, *namespaces).raw
        if abspath(normpath(path)) == '/':
            raw_info = raw_info.copy()
            raw_info['basic']['name'] = ''
        info = Info(raw_info)
        return info

    def listdir(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        dir_list = _fs.listdir(_path)
        return dir_list

    def lock(self):
        self._check()
        _fs = self.delegate_fs()
        return _fs.lock()

    def makedir(self, path, mode=0o777, recreate=False):
        self._check()
        _fs, _path = self.delegate_path(path)
        return _fs.makedir(_path, mode=mode, recreate=recreate)

    def move(self, src_path, dst_path, overwrite=False):
        # A custom move permits a potentially optimized code path
        if not overwrite and self.exists(dst_path):
            raise errors.DestinationExists(dst_path)
        src_fs, _src_path = self.delegate_path(src_path)
        dst_fs, _dst_path = self.delegate_path(dst_path)
        if src_fs is dst_fs:
            src_fs.move(_src_path, _dst_path, overwrite=overwrite)
        else:
            move_file(src_fs, _src_path, dst_fs, _dst_path)

    def openbin(self, path, mode='r', buffering=-1, **options):
        self._check()
        _fs, _path = self.delegate_path(path)
        bin_file = _fs.openbin(
            _path,
            mode=mode,
            buffering=-1,
            **options
        )
        return bin_file

    def remove(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.remove(_path)

    def removedir(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.removedir(_path)

    def scandir(self, path, namespaces=None):
        self._check()
        _fs, _path = self.delegate_path(path)
        for info in _fs.scandir(_path, namespaces=namespaces):
            yield info

    def setinfo(self, path, info):
        self._check()
        _fs, _path = self.delegate_path(path)
        return _fs.setinfo(_path, info)

    def settimes(self, path, accessed=None, modified=None):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.settimes(_path, accessed=accessed, modified=modified)

    def touch(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.touch(_path)

    def copy(self, src_path, dst_path):
        src_fs, _src_path = self.delegate_path(src_path)
        dst_fs, _dst_path = self.delegate_path(dst_path)
        copy_file(src_fs, _src_path, dst_fs, _dst_path)

    def create(self, path, wipe=False):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.create(_path, wipe=wipe)

    def desc(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        desc = _fs.desc(_path)
        return desc

    def exists(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        exists = _fs.exists(_path)
        return exists

    def filterdir(self,
                  path,
                  exclude_dirs=False,
                  exclude_files=False,
                  wildcards=None,
                  dir_wildcards=None,
                  namespaces=None):
        self._check()
        _fs, _path = self.delegate_path(path)
        iter_files = _fs.filterdir(
           _path,
           exclude_dirs=exclude_dirs,
           exclude_files=exclude_files,
           wildcards=wildcards,
           dir_wildcards=dir_wildcards,
           namespaces=namespaces
        )
        return iter_files

    def getbytes(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _bytes = _fs.getbytes(_path)
        return _bytes

    def gettext(self, path, encoding=None, errors=None, newline=None):
        self._check()
        _fs, _path = self.delegate_path(path)
        _text = _fs.gettext(_path,
                            encoding=encoding,
                            errors=errors,
                            newline=newline)
        return _text

    def getmeta(self, namespace='standard'):
        self._check()
        meta = self.delegate_fs().getmeta(namespace=namespace)
        return meta

    def getsize(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        size = _fs.getsize(_path)
        return size

    def getsyspath(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        sys_path = _fs.getsyspath(_path)
        return sys_path

    def gettype(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _type = _fs.gettype(_path)
        return _type

    def geturl(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        url = _fs.geturl(_path)
        return url

    def hassyspath(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        has_sys_path = _fs.hassyspath(_path)
        return has_sys_path

    def hasurl(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        has_url = _fs.hasurl(_path)
        return has_url

    def isdir(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _isdir = _fs.isdir(_path)
        return _isdir

    def isfile(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _isfile = _fs.isfile(_path)
        return _isfile

    def makedirs(self, path, recreate=False, mode=0o777):
        self._check()
        _fs, _path = self.delegate_path(path)
        return _fs.makedirs(_path, recreate=recreate, mode=mode)

    def open(self,
             path,
             mode='r',
             buffering=-1,
             encoding=None,
             errors=None,
             newline=None,
             line_buffering=False,
             **options):
        self._check()
        _fs, _path = self.delegate_path(path)
        open_file = _fs.open(
            _path,
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            line_buffering=line_buffering,
            **options
        )
        return open_file

    def opendir(self, path):
        from .subfs import SubFS
        info = self.getinfo(path)
        if not info.is_dir:
            raise errors.ResourceInvalid(
                "path should reference a directory"
            )
        return SubFS(self, path)

    def setbytes(self, path, contents):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.setbytes(_path, contents)

    def setfile(self,
                path,
                file,
                encoding=None,
                errors=None,
                newline=None):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.setfile(_path,
                    file,
                    encoding=encoding,
                    errors=errors,
                    newline=newline)

    def validatepath(self, path):
        self._check()
        _fs, _path = self.delegate_path(path)
        _fs.validatepath(_path)