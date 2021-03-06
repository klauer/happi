from happi import Device, EntryInfo, cache
from happi.loader import fill_template, from_container, load_devices
from happi.utils import create_alias


class TimeDevice(Device):
    days = EntryInfo("Number of days", enforce=int)


def test_fill_template(device):
    # Check that we can properly render a template
    template = "{{name}}"
    assert device.name == fill_template(template, device)
    # Check that we can enforce a type
    template = '{{z}}'
    z = fill_template(template, device, enforce_type=True)
    assert isinstance(z, float)
    # Check that we will convert a more complex template
    template = '{{z*100}}'
    assert z*100 == fill_template(template, device, enforce_type=True)
    # Check that we can handle non-jinja template
    template = "blah"
    assert template == fill_template(template, device, enforce_type=True)
    # Check that we do not enforce a NoneType
    template = "{{detailed_screen}}"
    assert fill_template(template, device, enforce_type=True) is None


def test_from_container():
    # Create a datetime device
    d = TimeDevice(name='Test', prefix='Tst:This:1', beamline='TST',
                   device_class='datetime.timedelta', args=list(), days=10,
                   kwargs={'days': '{{days}}', 'seconds': 30})
    td = from_container(d)
    # Now import datetime and check that we constructed ours correctly
    import datetime
    assert td == datetime.timedelta(days=10, seconds=30)


def test_caching():
    # Create a datetime device
    d = TimeDevice(name='Test', prefix='Tst:This:2', beamline='TST',
                   device_class='types.SimpleNamespace', args=list(), days=10,
                   kwargs={'days': '{{days}}', 'seconds': 30})
    td = from_container(d)
    assert d.prefix in cache
    assert id(td) == id(from_container(d))
    assert id(td) != id(from_container(d, use_cache=False))
    # Modify md and check we see a reload
    d.days = 12
    assert id(td) != id(from_container(d, use_cache=True))
    # Check with a device where metadata is unavailable
    d = TimeDevice(name='Test', prefix='Tst:Delta:3', beamline='TST',
                   device_class='datetime.timedelta', args=list(), days=10,
                   kwargs={'days': '{{days}}', 'seconds': 30})
    td = from_container(d)
    assert id(td) == id(from_container(d))
    assert id(td) != id(from_container(d, use_cache=False))


def test_add_md():
    d = Device(name='Test', prefix='Tst:This:3',
               beamline="TST", args=list(),
               device_class="happi.Device")
    obj = from_container(d, attach_md=True)
    assert obj.md.beamline == 'TST'
    assert obj.md.name == 'Test'


def test_load_devices():
    # Create a bunch of devices to load
    devs = [TimeDevice(name='Test 1', prefix='Tst1:This', beamline='TST',
                       device_class='datetime.timedelta', args=list(), days=10,
                       kwargs={'days': '{{days}}', 'seconds': 30}),
            TimeDevice(name='Test 2', prefix='Tst2:This', beamline='TST',
                       device_class='datetime.timedelta', args=list(), days=10,
                       kwargs={'days': '{{days}}', 'seconds': 30}),
            TimeDevice(name='Test 3', prefix='Tst3:This', beamline='TST',
                       device_class='datetime.timedelta', args=list(), days=10,
                       kwargs={'days': '{{days}}', 'seconds': 30}),
            Device(name='Bad', prefix='Not:Here', beamline='BAD',
                   device_class='non.existant')]
    # Load our devices
    space = load_devices(*devs, pprint=True)
    # Check all our devices are there
    assert all([create_alias(dev.name) in space.__dict__ for dev in devs])
    # Devices were loading properly or exceptions were stored
    import datetime
    assert space.test_1 == datetime.timedelta(days=10, seconds=30)
    assert isinstance(space.bad, ImportError)
