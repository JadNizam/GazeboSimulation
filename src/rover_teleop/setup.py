from setuptools import find_packages, setup

package_name = 'rover_teleop'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='You',
    maintainer_email='you@email.com',
    description='A highly responsive keyboard teleop node for rover',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rover_keyboard_teleop = rover_teleop.rover_keyboard_teleop:main',
            'simple_frontier_explorer = rover_teleop.simple_frontier_explorer:main',
            'cmd_vel_relay = rover_teleop.cmd_vel_relay:main',
        ],
    },
)
