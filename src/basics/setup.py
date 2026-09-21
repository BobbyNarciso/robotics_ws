from setuptools import find_packages, setup

package_name = 'basics'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='daniel',
    maintainer_email='danielsjohn2016@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'analog_subs = basics.analog_subs:main',
            'velocity_publisher = basics.velocity_publisher:main',
            'velocity_subscriber = basics.velocity_subscriber:main',
            'velocity_turtle_pub = basics.velocity_turtle_pub:main',
            'velocity_turtle_sub = basics.velocity_turtle_sub:main',
            'led_blink = basics.led_blink:main',
            'serial_bridge = basics.serial_bridge:main',
            'analog_serial_pub = basics.analog_serial_pub:main',
            'serial_pot = basics.serial_pot:main',                          'joystick_publisher = basics.joystick_publisher:main',
        ],
    },
)
