function pts = SelectPoints( image, howmany)
    pts = zeros(2, howmany);
    for i = 1:howmany,
        %redisplay image and title
        figure('Name',['Pick point ' int2str(i)]), imshow(image);
        
        %ask for pt
        pt = ginput(1);

        %add point to matrix
        pts(1,i) = pt(1);
        pts(2,i) = pt(2);
    end

end

