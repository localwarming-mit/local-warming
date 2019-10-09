howmany =2 ;
pts = zeros(2, 2);
for i = 1:howmany,
	%redisplay image and title
    imshow(image);
        
    %ask for pt
    pt = ginput(1);

    %add point to matrix
    pts(1,i) = pt(1);
    pts(2,i) = pt(2);
end

line(pts(1,:), pts(2,:));

while(1),
    imshow(image);
    line(pts(1,:), pts(2,:));
    pt = ginput(1);
    
    x1 = pts(:,1)
    x2 = pts(:,2)
    x0 = pt'
    n = sqrt(dot(x2-x1,x2-x1))
    %d = (x2(1)-x1(1)*(x1(2)-x0(2))-(x1(1)-x0(1))*(x2(2)-x1(2)))/n
    d = det([x2-x1,x1-x0])/n
    v = [x2(2)-x1(2); -(x2(1)-x1(1))]
    v = v ./ sqrt(dot(v,v));
    ot = x0-v*d
    hold on;
    plot(pt(1), pt(2), 'g+')
    
    plot(ot(1), ot(2), 'g+')
    
    %normalized coords
    nc = (ot-x1) ./ n
    p = sqrt(nc'*nc)
    pause;
end