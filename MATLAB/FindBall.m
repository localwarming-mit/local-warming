function [ballPos] = FindBall(im)
    hsv = rgb2hsv(im);
    h = hsv(:,:,1);
    v = hsv(:,:,3);

    %-----------
    %figure(1);
    %imshow(im);
    %-----------
    high_bnd = 1;
    low_bnd = 0.92;
    idmax = (h >= high_bnd);
    idmin = (h <= low_bnd);
    hi = ones(size(h));

    hi(idmax) = 0;
    hi(idmin) = 0;

    %figure(2);
   	%imshow(hi);
    %-----------
    high_bnd = 0.59;
    low_bnd = 0.5;
    idmax = (v >= high_bnd);
    idmin = (v <= low_bnd);
    vi = ones(size(v));

    vi(idmax) = 0;
    vi(idmin) = 0;

    %figure(3);
    %imshow(vi);
    %-----------
    out = vi.*hi;

    %figure(4);
    %imshow(out);
    %-----------

    CC = bwconncomp(out);
    numPixels = cellfun(@numel,CC.PixelIdxList);
    if(size(numPixels, 2) ~= 0),
        [biggest,idx] = max(numPixels);

        S = regionprops(CC,'Centroid');
        ballPos = S(idx).Centroid;
    else
        ballPos = [0 0];
    end
end