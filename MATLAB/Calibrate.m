%frame to select from
cam1frame = 1;
cam2frame = 1;
cam3frame = 1;
cam4frame = 1;

%get the actual frame data
cam1im = FrameFromMov('../cam1.mov', cam1frame);
cam2im = FrameFromMov('../cam2.mov', cam2frame);
cam3im = FrameFromMov('../cam3.mov', cam3frame);
cam4im = FrameFromMov('../cam4.mov', cam4frame);

%get points from mouse
pts1 = SelectPoints(cam1im, 4);
pts2 = SelectPoints(cam2im, 4);
pts3 = SelectPoints(cam3im, 4);
pts4 = SelectPoints(cam4im, 4);