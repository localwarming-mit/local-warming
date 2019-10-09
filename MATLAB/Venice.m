ballObj = VideoReader('bulbtest2.mp4');
% foundObj = VideoWriter('ballPos.avi');
% open(foundObj);
for i = 1:ballObj.NumberOfFrames,
    fprintf('Computing line: %d\n',i);
	%im = read(ballObj, 178);
    im = read(ballObj, i);
    %im = imresize(im, 0.5);
    figure(1);
    imshow(im);

    ballPos = FindBall(im);

    hold on
    plot(ballPos(1), ballPos(2), 'bo');
    %hfig = imgcf;
    out = getframe;
    out = out.cdata;
    imwrite(out, ['images/test' int2str(i) '.png']);
%     writeVideo(foundObj, out);
end

% close(foundObj);