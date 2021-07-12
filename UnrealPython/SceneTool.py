# read the transform files
f = open("D:/transform.txt", "r")
l = f.readline().strip("\n")
# get the selected asset
s = unreal.EditorUtilityLibrary.get_selected_assets()
while l:
    t = l.split(",")
    tt = unreal.Vector(float(t[0]), float(t[1]), float(t[2]))
    tr = unreal.Rotator(float(t[3]), float(t[4]), float(t[5]))
    ts = unreal.Vector(float(t[6]), float(t[7]), float(t[8]))
    st = unreal.Transform(tt, tr, ts)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(s[0], tt, tr)
    actor.set_actor_scale3d(ts)
    l = f.readline().strip("\n")

f.close()


# Export Actor Transform
s = unreal.EditorLevelLibrary.get_selected_level_actors()
output = ''
for actor in s :
    tt = actor.get_actor_location()
    tr = actor.get_actor_rotation()
    ts = actor.get_actor_scale3d()
    output += str(tt.x) + "," + str(tt.y) + "," + str(tt.z) + ","+ str(tr.roll) + "," + str(tr.pitch) + "," + str(tr.yaw) + "," + str(ts.x) + "," + str(ts.y) + "," + str(ts.z) + "\n"

f = open("D:/transform.txt", "w")
f.write(output)
f.close()



# import Actor Transform
f = open("D:/transform.txt", "r")
l = f.readline().strip("\n")
t = l.split(",")
tt = unreal.Vector(float(t[0]), float(t[1]), float(t[2]))
tr = unreal.Rotator( float(t[3]), float(t[4]), float(t[5]) )
ts = unreal.Vector(float(t[6]), float(t[7]), float(t[8]))
s = unreal.EditorLevelLibrary.get_selected_level_actors()
s[0].set_actor_location(tt, False, False)
s[0].set_actor_rotation(tr, False)
s[0].set_actor_scale3d(ts)
f.close()